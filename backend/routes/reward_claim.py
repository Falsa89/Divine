"""Pack 96 — Controlled Reward Claim Endpoint.

POST /api/rewards/claim?server_id=<sid>

Endpoint live-gated:
  * Kill switch env-var: `REWARD_CLAIM_LEDGER_LIVE_ENABLED` (default=`false`).
    Quando OFF -> 503 blocker `REWARD_CLAIM_LEDGER_LIVE_DISABLED`.
  * Allowlist da `utils.reward_source_registry` (`REWARD_SOURCE_REGISTRY`).
  * Idempotency token + ledger replay-safe via `reward_claim_ledger`.
  * Grants SOLO a `player_server_profiles.soft_currencies.*`. Premium/hard
    currency (`gems`) bloccata. Account-wide writes vietate.

Kill switch off by default per impostazione utente:
  * lo smoke E2E abilita esplicitamente via env override durante il test e poi
    ripristina il valore originale.

Sentinel: PUBLIC_SYNC_TAG_v110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_AND_CONTROLLED_CLAIM_PATHS
"""
import os
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from utils.reward_source_registry import (
    REWARD_SOURCE_REGISTRY,
    FORBIDDEN_REWARD_TYPES,
    lookup_source,
    is_source_live,
    get_grant_fn,
    list_allowlisted_sources,
    _PremiumGrantBlocked,
    _RewardTypeNotAllowed,
)


REWARD_CLAIM_LEDGER_KILL_SWITCH_ENV = "REWARD_CLAIM_LEDGER_LIVE_ENABLED"
LEDGER_COLLECTION = "reward_claim_ledger"


def _is_kill_switch_enabled() -> bool:
    """Default = false (Pack 96 user-mandated safety). Solo `true`/`1`/`yes` abilitano."""
    v = os.getenv(REWARD_CLAIM_LEDGER_KILL_SWITCH_ENV, "false")
    return str(v).strip().lower() in ("true", "1", "yes", "on")


class RewardClaimRequest(BaseModel):
    source: str
    reward_instance_id: str
    idempotency_token: str
    payload: Optional[Dict[str, Any]] = None


async def ensure_reward_claim_ledger_indices(db) -> Dict[str, Any]:
    """Crea (se non esiste) l'unique index idempotente sul ledger.

    SAFE: usa `create_index` con `unique=True`. MongoDB no-op se esiste lo stesso
    indice. NESSUN drop distruttivo. Se duplicati pre-esistenti causano
    DuplicateKey error in build, viene loggato e ritornato con `stopped=True`
    (caller deve fare triage manuale).
    """
    out: Dict[str, Any] = {"created_indices": [], "skipped": [], "stopped": False, "error": None}
    try:
        name = await db[LEDGER_COLLECTION].create_index(
            [("user_id", 1), ("server_id", 1), ("idempotency_token", 1)],
            unique=True, name="ux_user_server_idem_token_pack96", background=True,
        )
        out["created_indices"].append(name)
        # Secondary index for analytics queries (non-unique).
        name2 = await db[LEDGER_COLLECTION].create_index(
            [("applied_at", 1)], name="ix_applied_at_pack96", background=True,
        )
        out["created_indices"].append(name2)
    except Exception as e:
        out["stopped"] = True
        out["error"] = repr(e)
    return out


def register_reward_claim_routes(router, db, get_current_user, *_args, **_kwargs):
    """Pack 96 — controlled reward claim endpoint."""

    @router.get("/rewards/claim/health")
    async def reward_claim_health():
        return {
            "endpoint": "/api/rewards/claim",
            "kill_switch_env": REWARD_CLAIM_LEDGER_KILL_SWITCH_ENV,
            "live_enabled": _is_kill_switch_enabled(),
            "allowlisted_sources": list_allowlisted_sources(),
            "ledger_collection": LEDGER_COLLECTION,
            "pack_origin": "pack_96",
            "premium_grants_blocked": True,
            "reward_live_general": False,
            "release_readiness_claimed": False,
        }

    @router.post("/rewards/claim/preflight")
    async def reward_claim_preflight(current_user: dict = Depends(get_current_user)):
        """Idempotent index creation. Safe to call multiple times.

        Ritorna informazioni su index/registry. NON modifica reward_live general.
        """
        idx_result = await ensure_reward_claim_ledger_indices(db)
        return {
            "kill_switch_live_enabled": _is_kill_switch_enabled(),
            "index_creation": idx_result,
            "registry_size": len(REWARD_SOURCE_REGISTRY),
            "allowlisted_sources": list_allowlisted_sources(),
            "forbidden_reward_types": sorted(FORBIDDEN_REWARD_TYPES),
            "_slc_pack_96_reward_claim_preflight": True,
        }

    @router.post("/rewards/claim")
    async def reward_claim(
        req: RewardClaimRequest,
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]

        # === 1. Kill switch check (default-OFF) ===
        if not _is_kill_switch_enabled():
            raise HTTPException(503, detail={
                "blocker": "REWARD_CLAIM_LEDGER_LIVE_DISABLED",
                "kill_switch_env": REWARD_CLAIM_LEDGER_KILL_SWITCH_ENV,
                "reason": "Pack 96 reward claim ledger live execute richiede explicit env override. Default OFF per safety.",
                "reward_live_general": False,
            })

        # === 2. Server scope check ===
        if not server_id or not isinstance(server_id, str) or not server_id.strip():
            raise HTTPException(400, detail={"blocker": "SERVER_ID_REQUIRED",
                                             "endpoint": "/api/rewards/claim"})
        sid = server_id.strip()

        # === 3. PSP check ===
        psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
        if not psp:
            raise HTTPException(409, detail={"blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
                                             "server_id": sid})

        # === 4. Idempotency token validation ===
        if not req.idempotency_token or not isinstance(req.idempotency_token, str) \
                or len(req.idempotency_token) < 8:
            raise HTTPException(400, detail={"blocker": "IDEMPOTENCY_TOKEN_REQUIRED",
                                             "min_length": 8})

        # === 5. Source registry lookup (allowlist enforcement) ===
        src = lookup_source(req.source)
        if not src:
            raise HTTPException(422, detail={
                "blocker": "REWARD_SOURCE_NOT_ALLOWLISTED",
                "source": req.source,
                "allowlist": list_allowlisted_sources(),
            })
        if not is_source_live(req.source):
            raise HTTPException(422, detail={
                "blocker": "REWARD_SOURCE_NOT_LIVE",
                "source": req.source,
            })
        if src.get("server_scoped") and not sid:
            raise HTTPException(400, detail={"blocker": "SOURCE_REQUIRES_SERVER_SCOPE",
                                             "source": req.source})

        # === 6. Replay check (no double grant) ===
        existing = await db[LEDGER_COLLECTION].find_one({
            "user_id": uid, "server_id": sid,
            "idempotency_token": req.idempotency_token,
        })
        if existing:
            # Strip mongo _id for JSON safety.
            existing.pop("_id", None)
            return {
                "idempotent_replay": True,
                "server_id": sid,
                "source": existing.get("claim_source"),
                "claim_key": existing.get("claim_key"),
                "rewards": existing.get("rewards"),
                "applied_at": existing.get("applied_at").isoformat() if existing.get("applied_at") else None,
                "pack_96_controlled_claim": True,
                "reward_live_general": False,
            }

        # === 7. Grant engine guard ===
        grant_fn = get_grant_fn(req.source)
        if grant_fn is None:
            raise HTTPException(500, detail={"blocker": "GRANT_FN_MISSING",
                                             "source": req.source})

        payload = req.payload or {}
        # Hard reject premium types prima del grant
        for k in list(payload.keys()):
            if k in FORBIDDEN_REWARD_TYPES:
                raise HTTPException(422, detail={
                    "blocker": "PREMIUM_GRANT_BLOCKED",
                    "reward_type": k,
                    "source": req.source,
                })

        try:
            inc_set = grant_fn(db, uid, sid, payload)
        except _PremiumGrantBlocked as ex:
            raise HTTPException(422, detail={"blocker": "PREMIUM_GRANT_BLOCKED",
                                             "reward_type": ex.reward_key,
                                             "source": req.source})
        except _RewardTypeNotAllowed as ex:
            raise HTTPException(422, detail={"blocker": "REWARD_TYPE_NOT_ALLOWED",
                                             "reward_type": ex.reward_key,
                                             "source": req.source})

        # === 8. Apply server-scoped grant to PSP (atomic $inc) ===
        granted_summary: Dict[str, int] = {}
        if inc_set:
            await db.player_server_profiles.update_one(
                {"user_id": uid, "server_id": sid},
                {"$inc": inc_set,
                 "$set": {"_slc_pack_96_last_claim_ts": datetime.utcnow()}},
            )
            # Build summary {soft_currency: amount}
            for path_k, amt in inc_set.items():
                key = path_k.split(".", 1)[-1] if "." in path_k else path_k
                granted_summary[key] = amt

        # === 9. Ledger insert (audit) ===
        claim_key = f"{req.source}_{req.reward_instance_id}"
        ledger_row = {
            "id": str(uuid.uuid4()),
            "user_id": uid,
            "server_id": sid,
            "claim_source": req.source,
            "claim_key": claim_key,
            "reward_instance_id": req.reward_instance_id,
            "idempotency_token": req.idempotency_token,
            "rewards": {
                "server_scoped": granted_summary,
                "account_wide": {},
                "live_grant": True,
            },
            "victory": True,
            "applied_at": datetime.utcnow(),
            "_slc_pack_96_controlled_claim": True,
            "_slc_pack_96_grant_engine_guard": True,
            "_slc_pack_95_reward_claim_ledger": True,
        }
        try:
            await db[LEDGER_COLLECTION].insert_one(ledger_row)
        except Exception as e:
            # In rare race: unique index hit -> treat as replay.
            existing = await db[LEDGER_COLLECTION].find_one({
                "user_id": uid, "server_id": sid,
                "idempotency_token": req.idempotency_token,
            })
            if existing:
                # Compensate the grant we just applied (subtract back) — safest path:
                if inc_set:
                    rev = {k: -v for k, v in inc_set.items()}
                    await db.player_server_profiles.update_one(
                        {"user_id": uid, "server_id": sid}, {"$inc": rev},
                    )
                existing.pop("_id", None)
                return {
                    "idempotent_replay": True,
                    "server_id": sid,
                    "source": existing.get("claim_source"),
                    "claim_key": existing.get("claim_key"),
                    "rewards": existing.get("rewards"),
                    "race_compensation_applied": True,
                    "pack_96_controlled_claim": True,
                }
            raise HTTPException(500, detail={"blocker": "LEDGER_INSERT_FAILED",
                                             "error": repr(e)})

        return {
            "idempotent_replay": False,
            "server_id": sid,
            "source": req.source,
            "claim_key": claim_key,
            "rewards": ledger_row["rewards"],
            "applied_at": ledger_row["applied_at"].isoformat(),
            "pack_96_controlled_claim": True,
            "reward_live_general": False,
            "premium_grant_blocked": True,
        }
