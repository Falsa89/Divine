"""Pack 97 — Daily Login Claim endpoint.

Thin endpoint `POST /api/daily-login/claim?server_id=<sid>` che routa al reward
claim ledger pipeline (riusa logica Pack 96) con:

  * source forzata a `daily_login_claim`
  * `claim_key` calcolato server-side: `daily_login_<server_id>_<YYYY-MM-DD UTC>`
  * `idempotency_token` deterministico SHA1 del claim_key (client value ignorato)
  * Per-source kill switch env `DAILY_LOGIN_CLAIM_ENABLED` (default OFF) IN AND col
    global `REWARD_CLAIM_LEDGER_LIVE_ENABLED` (default OFF)
  * Unique index addizionale su `(user_id, server_id, claim_key)` per garanzia DB
  * Reward fisso definito server-side da `_grant_daily_login_to_psp` (payload client ignorato)
  * Test-only `_test_day_override` query param accettato SOLO se user marker
    `pack_97_test_artifact=true` su users collection.
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
# Pack 100 — bridge eventi gameplay safe -> tracker daily quest (no reward grant).
from utils.daily_quest_events import record_daily_quest_event as _record_dq_event

GLOBAL_KILL_SWITCH_ENV = "REWARD_CLAIM_LEDGER_LIVE_ENABLED"
DAILY_KILL_SWITCH_ENV = "DAILY_LOGIN_CLAIM_ENABLED"
LEDGER_COLLECTION = "reward_claim_ledger"
DAILY_SOURCE = "daily_login_claim"


def _truthy(v: Optional[str]) -> bool:
    return str(v or "false").strip().lower() in ("true", "1", "yes", "on")


def _global_kill_switch_on() -> bool:
    return _truthy(os.getenv(GLOBAL_KILL_SWITCH_ENV))


def _daily_kill_switch_on() -> bool:
    return _truthy(os.getenv(DAILY_KILL_SWITCH_ENV))


def _both_switches_on() -> bool:
    return _global_kill_switch_on() and _daily_kill_switch_on()


def compute_daily_claim_key(server_id: str, day_iso: Optional[str] = None) -> str:
    """Restituisce il claim_key deterministico per il daily login.

    Format: `daily_login_<server_id>_<YYYY-MM-DD UTC>`. Se `day_iso` viene fornito
    (modalita' test-only), viene usato al posto della UTC corrente.
    """
    if day_iso:
        # Validate format strict YYYY-MM-DD
        try:
            datetime.strptime(day_iso, "%Y-%m-%d")
        except Exception:
            raise HTTPException(400, detail={"blocker": "INVALID_DAY_OVERRIDE_FORMAT"})
        return f"daily_login_{server_id}_{day_iso}"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"daily_login_{server_id}_{today}"


def derive_idempotency_token_from_claim_key(claim_key: str) -> str:
    return hashlib.sha1(claim_key.encode("utf-8")).hexdigest()


async def ensure_daily_login_indices(db) -> Dict[str, Any]:
    """Crea unique index per garantire 1 claim/giorno/server/utente a livello DB.

    Index: `(user_id, server_id, claim_key)` partial filter su `claim_source = daily_login_claim`.
    Idempotent, no destructive drop.
    """
    out: Dict[str, Any] = {"created": [], "stopped": False, "error": None}
    try:
        name = await db[LEDGER_COLLECTION].create_index(
            [("user_id", 1), ("server_id", 1), ("claim_key", 1)],
            unique=True,
            partialFilterExpression={"claim_source": DAILY_SOURCE},
            name="ux_user_server_claimkey_daily_login_pack97",
            background=True,
        )
        out["created"].append(name)
    except Exception as e:
        out["stopped"] = True
        out["error"] = repr(e)
    return out


class DailyLoginClaimRequest(BaseModel):
    # Pack 97: il client puo' inviare un client_token informativo (loggato per audit)
    # ma il backend lo IGNORA per la idempotenza (deterministico dal claim_key).
    client_token: Optional[str] = None


def register_daily_login_claim_routes(router, db, get_current_user, *_args, **_kwargs):

    @router.get("/daily-login/claim/health")
    async def daily_login_health():
        return {
            "endpoint": "/api/daily-login/claim",
            "global_kill_switch_env": GLOBAL_KILL_SWITCH_ENV,
            "global_kill_switch_live_enabled": _global_kill_switch_on(),
            "daily_kill_switch_env": DAILY_KILL_SWITCH_ENV,
            "daily_kill_switch_live_enabled": _daily_kill_switch_on(),
            "claim_executable": _both_switches_on(),
            "source": DAILY_SOURCE,
            "source_registered": DAILY_SOURCE in REWARD_SOURCE_REGISTRY,
            "fixed_reward": {"mission_coins": 10, "honor": 5},
            "pack_origin": "pack_97",
            "pack_100_event_bridge_enabled": True,
            "pack_100_event_emitted_on_success": "daily_login_claim_success",
            "pack_100_event_target_quest": "daily_quest_1",
            "release_readiness_claimed": False,
            "reward_live_general": False,
        }

    @router.post("/daily-login/claim/preflight")
    async def daily_login_preflight(current_user: dict = Depends(get_current_user)):
        idx = await ensure_daily_login_indices(db)
        return {
            "global_kill_switch_on": _global_kill_switch_on(),
            "daily_kill_switch_on": _daily_kill_switch_on(),
            "claim_executable": _both_switches_on(),
            "indices": idx,
            "_slc_pack_97_daily_login_preflight": True,
        }

    @router.post("/daily-login/claim")
    async def daily_login_claim(
        req: DailyLoginClaimRequest,
        server_id: str = None,
        _test_day_override: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]

        # 1. Both kill switches must be ON
        if not _global_kill_switch_on():
            raise HTTPException(503, detail={
                "blocker": "REWARD_CLAIM_LEDGER_LIVE_DISABLED",
                "kill_switch_env": GLOBAL_KILL_SWITCH_ENV,
                "claim_executable": False,
            })
        if not _daily_kill_switch_on():
            raise HTTPException(503, detail={
                "blocker": "DAILY_LOGIN_CLAIM_DISABLED",
                "kill_switch_env": DAILY_KILL_SWITCH_ENV,
                "claim_executable": False,
            })

        # 2. server_id required + PSP check
        if not server_id or not isinstance(server_id, str) or not server_id.strip():
            raise HTTPException(400, detail={"blocker": "SERVER_ID_REQUIRED"})
        sid = server_id.strip()
        psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
        if not psp:
            raise HTTPException(409, detail={"blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
                                             "server_id": sid})

        # 3. Test-only day override: allowed ONLY if user is marked pack_97_test_artifact=true
        day_override = None
        if _test_day_override:
            user_doc = await db.users.find_one({"id": uid})
            if not user_doc or not user_doc.get("pack_97_test_artifact"):
                raise HTTPException(403, detail={
                    "blocker": "DAY_OVERRIDE_FORBIDDEN_FOR_NON_TEST_USER",
                    "reason": "_test_day_override accettato SOLO se users.pack_97_test_artifact=true",
                })
            day_override = _test_day_override.strip()

        # 4. Source registry lookup (must be live)
        src = lookup_source(DAILY_SOURCE)
        if not src or not is_source_live(DAILY_SOURCE):
            raise HTTPException(422, detail={"blocker": "REWARD_SOURCE_NOT_ALLOWLISTED",
                                             "source": DAILY_SOURCE})

        # 5. Compute deterministic claim_key + idempotency_token server-side
        claim_key = compute_daily_claim_key(sid, day_override)
        idem_token = derive_idempotency_token_from_claim_key(claim_key)

        # 6. Replay check via claim_key (anti-double-grant per day)
        existing = await db[LEDGER_COLLECTION].find_one({
            "user_id": uid, "server_id": sid,
            "claim_source": DAILY_SOURCE, "claim_key": claim_key,
        })
        if existing:
            existing.pop("_id", None)
            # Pack 100 — bridge to daily quest tracker (idempotente, no-op se gia` completed/claimed).
            dq_event = await _record_dq_event(
                db, uid, sid, "daily_login_claim_success",
                payload={"replay": True, "claim_key": claim_key},
                source_route="daily_login_claim",
                day_iso=day_override,
            )
            return {
                "idempotent_replay": True, "server_id": sid,
                "claim_source": DAILY_SOURCE, "claim_key": claim_key,
                "rewards": existing.get("rewards"),
                "applied_at": existing.get("applied_at").isoformat() if existing.get("applied_at") else None,
                "next_claim_available_after_utc_midnight": True,
                "pack_97_daily_login_claim": True,
                "reward_live_general": False,
                "daily_quest_event_bridge": dq_event,
                "pack_100_event_bridge_attempted": True,
            }

        # 7. Grant via registry fn (payload client ignorato; reward fisso)
        grant_fn = get_grant_fn(DAILY_SOURCE)
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

        # 8. Apply atomic $inc to PSP.soft_currencies ONLY (no users.* mutation)
        granted_summary: Dict[str, int] = {}
        if inc_set:
            await db.player_server_profiles.update_one(
                {"user_id": uid, "server_id": sid},
                {"$inc": inc_set,
                 "$set": {"_slc_pack_97_last_daily_claim_ts": datetime.utcnow()}},
            )
            for path_k, amt in inc_set.items():
                key = path_k.split(".", 1)[-1] if "." in path_k else path_k
                granted_summary[key] = amt

        # 9. Insert ledger row (anti-double-grant via unique index)
        ledger_row = {
            "id": str(uuid.uuid4()),
            "user_id": uid, "server_id": sid,
            "claim_source": DAILY_SOURCE,
            "claim_key": claim_key,
            "reward_instance_id": claim_key,  # server-derived
            "idempotency_token": idem_token,
            "client_token_received": (req.client_token if req else None),  # audit only
            "rewards": {
                "server_scoped": granted_summary,
                "account_wide": {},
                "live_grant": True,
            },
            "victory": True,
            "applied_at": datetime.utcnow(),
            "_slc_pack_97_daily_login_claim": True,
            "_slc_pack_97_server_side_claim_key": True,
            "_slc_pack_96_controlled_claim": True,
            "_slc_pack_95_reward_claim_ledger": True,
        }
        try:
            await db[LEDGER_COLLECTION].insert_one(ledger_row)
        except Exception as e:
            # Race: another concurrent claim won; compensate the $inc just applied + return replay
            existing = await db[LEDGER_COLLECTION].find_one({
                "user_id": uid, "server_id": sid,
                "claim_source": DAILY_SOURCE, "claim_key": claim_key,
            })
            if existing:
                if inc_set:
                    rev = {k: -v for k, v in inc_set.items()}
                    await db.player_server_profiles.update_one(
                        {"user_id": uid, "server_id": sid}, {"$inc": rev},
                    )
                existing.pop("_id", None)
                return {
                    "idempotent_replay": True, "server_id": sid,
                    "claim_source": DAILY_SOURCE, "claim_key": claim_key,
                    "rewards": existing.get("rewards"),
                    "race_compensation_applied": True,
                    "pack_97_daily_login_claim": True,
                }
            raise HTTPException(500, detail={"blocker": "LEDGER_INSERT_FAILED",
                                             "error": repr(e)})

        # Pack 100 — bridge to daily quest tracker (no reward grant, server-scoped, kill-switch-respecting).
        dq_event = await _record_dq_event(
            db, uid, sid, "daily_login_claim_success",
            payload={"replay": False, "claim_key": claim_key},
            source_route="daily_login_claim",
            day_iso=day_override,
        )

        return {
            "idempotent_replay": False, "server_id": sid,
            "claim_source": DAILY_SOURCE, "claim_key": claim_key,
            "rewards": ledger_row["rewards"],
            "applied_at": ledger_row["applied_at"].isoformat(),
            "next_claim_available_after_utc_midnight": True,
            "pack_97_daily_login_claim": True,
            "reward_live_general": False,
            "premium_grant_blocked": True,
            "daily_quest_event_bridge": dq_event,
            "pack_100_event_bridge_attempted": True,
        }
