"""Pack 98+99 — Daily Quest Completion Claim endpoint.

POST /api/daily-quest/claim?server_id=<sid>&quest_id=<qid>

Pack 98 SAFETY (preservata):
  * Source `daily_quest_completion_claim` registrata.
  * Kill switches AND (entrambi default OFF):
      - REWARD_CLAIM_LEDGER_LIVE_ENABLED (Pack 96)
      - DAILY_QUEST_CLAIM_ENABLED       (Pack 98)
  * `claim_key = daily_quest_<server_id>_<quest_id>_<YYYY-MM-DD UTC>`
    server-side deterministic.
  * Unique partial index su (user_id, server_id, claim_key) per
    `claim_source=daily_quest_completion_claim`.
  * `idempotency_token = sha1(claim_key)` (client-provided ignorato).
  * Grant solo su `player_server_profiles.soft_currencies.*`. No premium.

Pack 99 SAFETY (nuova):
  * **Completion runtime tracker server-side**: il claim consulta lo
    stato `daily_quest_progress` via
    `routes.daily_quest_tracker.is_quest_completed(...)`. Se lo stato non
    e' `completed`/`claimed` il claim ritorna 409
    `DAILY_QUEST_COMPLETION_REQUIRED` (no client spoofing possibile).
  * Dopo grant riuscito il tracker passa a `claimed` con `claimed_at`.
  * Bypass legacy Pack 98 `test_completion_proof=true` + marker
    `pack_98_test_artifact=true` MANTENUTO solo per compatibilita`
    storica delle smoke pre-Pack-99 (richiesto da test_completion_proof
    esplicito). Il path nuovo passa per il tracker.
"""
import hashlib
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from utils.reward_source_registry import (
    REWARD_SOURCE_REGISTRY,
    FORBIDDEN_REWARD_TYPES,
    lookup_source,
    is_source_live,
    get_grant_fn,
    _PremiumGrantBlocked,
    _RewardTypeNotAllowed,
)
# Pack 99 — collegamento al runtime tracker server-side.
from routes.daily_quest_tracker import (
    is_quest_completed as _tracker_is_completed,
    mark_quest_claimed as _tracker_mark_claimed,
    USER_TEST_MARKER as PACK_99_USER_TEST_MARKER,
)

GLOBAL_KILL_SWITCH_ENV = "REWARD_CLAIM_LEDGER_LIVE_ENABLED"
QUEST_KILL_SWITCH_ENV = "DAILY_QUEST_CLAIM_ENABLED"
LEDGER_COLLECTION = "reward_claim_ledger"
QUEST_SOURCE = "daily_quest_completion_claim"
QUEST_ID_WHITELIST = {"daily_quest_1", "daily_quest_2", "daily_quest_3"}


def _truthy(v: Optional[str]) -> bool:
    return str(v or "false").strip().lower() in ("true", "1", "yes", "on")


def _global_on() -> bool:
    return _truthy(os.getenv(GLOBAL_KILL_SWITCH_ENV))


def _quest_on() -> bool:
    return _truthy(os.getenv(QUEST_KILL_SWITCH_ENV))


def _both_on() -> bool:
    return _global_on() and _quest_on()


def compute_quest_claim_key(server_id: str, quest_id: str,
                            day_iso: Optional[str] = None) -> str:
    if day_iso:
        try:
            datetime.strptime(day_iso, "%Y-%m-%d")
        except Exception:
            raise HTTPException(400, detail={"blocker": "INVALID_DAY_OVERRIDE_FORMAT"})
        return f"daily_quest_{server_id}_{quest_id}_{day_iso}"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"daily_quest_{server_id}_{quest_id}_{today}"


def derive_token(claim_key: str) -> str:
    return hashlib.sha1(claim_key.encode("utf-8")).hexdigest()


async def ensure_daily_quest_indices(db) -> Dict[str, Any]:
    out: Dict[str, Any] = {"created": [], "stopped": False, "error": None}
    try:
        name = await db[LEDGER_COLLECTION].create_index(
            [("user_id", 1), ("server_id", 1), ("claim_key", 1)],
            unique=True,
            partialFilterExpression={"claim_source": QUEST_SOURCE},
            name="ux_user_server_claimkey_daily_quest_pack98",
            background=True,
        )
        out["created"].append(name)
    except Exception as e:
        out["stopped"] = True
        out["error"] = repr(e)
    return out


class DailyQuestClaimRequest(BaseModel):
    client_token: Optional[str] = None
    # Pack 98: completion proof.
    # `False` (default) => blocker DAILY_QUEST_COMPLETION_REQUIRED per utenti reali.
    # `True` => permesso SOLO se user marker pack_98_test_artifact=true.
    test_completion_proof: Optional[bool] = False


def register_daily_quest_claim_routes(router, db, get_current_user, *_a, **_kw):

    @router.get("/daily-quest/claim/health")
    async def daily_quest_health():
        return {
            "endpoint": "/api/daily-quest/claim",
            "global_kill_switch_env": GLOBAL_KILL_SWITCH_ENV,
            "global_kill_switch_live_enabled": _global_on(),
            "quest_kill_switch_env": QUEST_KILL_SWITCH_ENV,
            "quest_kill_switch_live_enabled": _quest_on(),
            "claim_executable": _both_on(),
            "source": QUEST_SOURCE,
            "ready_status": "READY_TRACKER_GATED",
            "quest_id_whitelist": sorted(QUEST_ID_WHITELIST),
            "completion_proof_required_for_real_users": True,
            "completion_proof_test_only_via_marker": "pack_98_test_artifact",
            "completion_tracker_required_for_real_users": True,
            "completion_tracker_marker_required": PACK_99_USER_TEST_MARKER,
            "completion_tracker_collection": "daily_quest_progress",
            "fixed_reward": {"mission_coins": 15, "honor": 8},
            "pack_origin": "pack_98",
            "pack_99_tracker_integrated": True,
            "pack_100_event_bridge_integrated": True,
            "pack_100_quest_real_completion_event_status": {
                "daily_quest_1": "REAL_COMPLETION_EVENT_READY",
                "daily_quest_2": "COMPLETION_RUNTIME_DEFERRED",
                "daily_quest_3": "COMPLETION_RUNTIME_DEFERRED",
            },
            "release_readiness_claimed": False,
            "reward_live_general": False,
        }

    @router.post("/daily-quest/claim/preflight")
    async def daily_quest_preflight(current_user: dict = Depends(get_current_user)):
        idx = await ensure_daily_quest_indices(db)
        return {
            "global_kill_switch_on": _global_on(),
            "quest_kill_switch_on": _quest_on(),
            "claim_executable": _both_on(),
            "indices": idx,
            "quest_id_whitelist": sorted(QUEST_ID_WHITELIST),
            "_slc_pack_98_daily_quest_preflight": True,
        }

    @router.post("/daily-quest/claim")
    async def daily_quest_claim(
        req: DailyQuestClaimRequest,
        server_id: str = None,
        quest_id: str = None,
        _test_day_override: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]

        # 1. Both kill switches AND
        if not _global_on():
            raise HTTPException(503, detail={
                "blocker": "REWARD_CLAIM_LEDGER_LIVE_DISABLED",
                "kill_switch_env": GLOBAL_KILL_SWITCH_ENV,
            })
        if not _quest_on():
            raise HTTPException(503, detail={
                "blocker": "DAILY_QUEST_CLAIM_DISABLED",
                "kill_switch_env": QUEST_KILL_SWITCH_ENV,
            })

        # 2. server_id required
        if not server_id or not isinstance(server_id, str) or not server_id.strip():
            raise HTTPException(400, detail={"blocker": "SERVER_ID_REQUIRED"})
        sid = server_id.strip()

        # 3. quest_id required + whitelist
        if not quest_id or not isinstance(quest_id, str) or not quest_id.strip():
            raise HTTPException(400, detail={"blocker": "QUEST_ID_REQUIRED"})
        qid = quest_id.strip()
        if qid not in QUEST_ID_WHITELIST:
            raise HTTPException(422, detail={
                "blocker": "QUEST_ID_NOT_WHITELISTED",
                "quest_id": qid,
                "allowlist": sorted(QUEST_ID_WHITELIST),
            })

        # 4. PSP required
        psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
        if not psp:
            raise HTTPException(409, detail={"blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
                                             "server_id": sid})

        # 5. Completion proof check (Pack 98 + Pack 99):
        #
        # Path A (legacy Pack 98 fallback test-only):
        #   - `test_completion_proof=true` + user marker `pack_98_test_artifact=true`
        #     => bypass diretto (mantenuto per le smoke pre-Pack-99).
        #
        # Path B (Pack 99 nuovo - runtime tracker server-side):
        #   - Si consulta `daily_quest_progress` via tracker.is_quest_completed().
        #   - Se lo stato e' `completed` (o `claimed` per replay idempotente),
        #     il claim e' autorizzato.
        #   - Se lo stato e' `not_started`/`in_progress`/assente, blocker
        #     `DAILY_QUEST_COMPLETION_REQUIRED` (no client spoofing possibile).
        #
        # NOTA: il tracker completion endpoint e' ancora test-only finche` non
        # esiste un runtime di gameplay reale (vedi Pack 99 SOT). Pertanto i real
        # player NON possono completare quest via API ad oggi e quindi NON
        # possono nemmeno claimare reward => safety invariata.
        user_doc = await db.users.find_one({"id": uid})
        is_pack_98_marked = bool(user_doc and user_doc.get("pack_98_test_artifact"))

        # Day override va computato qui per riusarlo nel tracker lookup e nella claim_key.
        day_override = None
        if _test_day_override:
            if not (is_pack_98_marked or user_doc.get(PACK_99_USER_TEST_MARKER)):
                raise HTTPException(403, detail={
                    "blocker": "DAY_OVERRIDE_FORBIDDEN_FOR_NON_TEST_USER",
                })
            day_override = _test_day_override.strip()

        completion_proof_source = None
        if req.test_completion_proof:
            # Path A - legacy bypass Pack 98 (richiede marker pack_98_test_artifact)
            if not is_pack_98_marked:
                raise HTTPException(403, detail={
                    "blocker": "TEST_COMPLETION_PROOF_FORBIDDEN_FOR_NON_TEST_USER",
                    "reason": "test_completion_proof accettato SOLO con marker pack_98_test_artifact=true",
                })
            completion_proof_source = "test_only_marker"
        else:
            # Path B - Pack 99 runtime tracker enforcement (no client spoofing)
            completed = await _tracker_is_completed(db, uid, sid, qid, day_override)
            if not completed:
                raise HTTPException(409, detail={
                    "blocker": "DAILY_QUEST_COMPLETION_REQUIRED",
                    "quest_id": qid,
                    "ready_status": "READY_TRACKER_GATED",
                    "reason": (
                        "Pack 99 tracker server-side richiede state=completed "
                        "sulla collection `daily_quest_progress` prima di concedere il "
                        "reward. Il client NON puo` impostare lo stato direttamente. "
                        "Real player ricevono il completamento solo quando il runtime "
                        "di gameplay diventera` authoritative."
                    ),
                    "tracker_collection": "daily_quest_progress",
                })
            completion_proof_source = "runtime_tracker"

        # 7. Source registry lookup
        src = lookup_source(QUEST_SOURCE)
        if not src or not is_source_live(QUEST_SOURCE):
            raise HTTPException(422, detail={"blocker": "REWARD_SOURCE_NOT_ALLOWLISTED",
                                             "source": QUEST_SOURCE})

        # 8. Compute server-side claim_key
        claim_key = compute_quest_claim_key(sid, qid, day_override)
        idem_token = derive_token(claim_key)

        # 9. Replay check
        existing = await db[LEDGER_COLLECTION].find_one({
            "user_id": uid, "server_id": sid,
            "claim_source": QUEST_SOURCE, "claim_key": claim_key,
        })
        if existing:
            existing.pop("_id", None)
            return {
                "idempotent_replay": True, "server_id": sid, "quest_id": qid,
                "claim_source": QUEST_SOURCE, "claim_key": claim_key,
                "rewards": existing.get("rewards"),
                "applied_at": existing.get("applied_at").isoformat() if existing.get("applied_at") else None,
                "pack_98_daily_quest_claim": True,
                "reward_live_general": False,
            }

        # 10. Grant
        grant_fn = get_grant_fn(QUEST_SOURCE)
        if grant_fn is None:
            raise HTTPException(500, detail={"blocker": "GRANT_FN_MISSING"})
        try:
            inc_set = grant_fn(db, uid, sid, {})
        except _PremiumGrantBlocked as ex:
            raise HTTPException(422, detail={"blocker": "PREMIUM_GRANT_BLOCKED",
                                             "reward_type": ex.reward_key})
        except _RewardTypeNotAllowed as ex:
            raise HTTPException(422, detail={"blocker": "REWARD_TYPE_NOT_ALLOWED",
                                             "reward_type": ex.reward_key})

        # 11. Apply $inc to PSP only
        granted_summary: Dict[str, int] = {}
        if inc_set:
            await db.player_server_profiles.update_one(
                {"user_id": uid, "server_id": sid},
                {"$inc": inc_set,
                 "$set": {"_slc_pack_98_last_quest_claim_ts": datetime.utcnow()}},
            )
            for path_k, amt in inc_set.items():
                key = path_k.split(".", 1)[-1] if "." in path_k else path_k
                granted_summary[key] = amt

        # 12. Ledger insert
        ledger_row = {
            "id": str(uuid.uuid4()),
            "user_id": uid, "server_id": sid,
            "claim_source": QUEST_SOURCE,
            "claim_key": claim_key,
            "reward_instance_id": f"{qid}_{claim_key}",
            "quest_id": qid,
            "idempotency_token": idem_token,
            "client_token_received": (req.client_token if req else None),
            "rewards": {
                "server_scoped": granted_summary,
                "account_wide": {},
                "live_grant": True,
            },
            "victory": True,
            "applied_at": datetime.utcnow(),
            "_slc_pack_98_daily_quest_claim": True,
            "_slc_pack_98_server_side_claim_key": True,
            "_slc_pack_98_completion_proof_marker_required": True,
            "_slc_pack_99_completion_source": completion_proof_source,
            "_slc_pack_99_tracker_gated": True,
            "_slc_pack_96_controlled_claim": True,
            "_slc_pack_95_reward_claim_ledger": True,
        }
        try:
            await db[LEDGER_COLLECTION].insert_one(ledger_row)
        except Exception as e:
            # Race fallback
            existing = await db[LEDGER_COLLECTION].find_one({
                "user_id": uid, "server_id": sid,
                "claim_source": QUEST_SOURCE, "claim_key": claim_key,
            })
            if existing:
                if inc_set:
                    rev = {k: -v for k, v in inc_set.items()}
                    await db.player_server_profiles.update_one(
                        {"user_id": uid, "server_id": sid}, {"$inc": rev},
                    )
                existing.pop("_id", None)
                return {
                    "idempotent_replay": True, "server_id": sid, "quest_id": qid,
                    "claim_source": QUEST_SOURCE, "claim_key": claim_key,
                    "rewards": existing.get("rewards"),
                    "race_compensation_applied": True,
                    "pack_98_daily_quest_claim": True,
                }
            raise HTTPException(500, detail={"blocker": "LEDGER_INSERT_FAILED",
                                             "error": repr(e)})

        # 13. Transizione tracker Pack 99: completed -> claimed (idempotent)
        try:
            await _tracker_mark_claimed(db, uid, sid, qid, day_override)
        except Exception:
            # Non-blocking: il claim e' gia` registrato a ledger; tracker e'
            # solo per audit/idempotency state. Errore silente.
            pass

        return {
            "idempotent_replay": False, "server_id": sid, "quest_id": qid,
            "claim_source": QUEST_SOURCE, "claim_key": claim_key,
            "rewards": ledger_row["rewards"],
            "applied_at": ledger_row["applied_at"].isoformat(),
            "pack_98_daily_quest_claim": True,
            "pack_99_tracker_state_after_claim": "claimed",
            "completion_proof_used": completion_proof_source,
            "reward_live_general": False,
            "premium_grant_blocked": True,
        }
