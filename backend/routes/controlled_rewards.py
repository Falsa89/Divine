"""Pack 106 — Controlled Rewards (mail / achievement / daily-weekly).

Endpoints registrati su prefix `/api/controlled-rewards`:

  * GET  /api/controlled-rewards/health
  * GET  /api/controlled-rewards/catalog
  * POST /api/controlled-rewards/mail/claim?server_id=<sid>
  * POST /api/controlled-rewards/achievement/claim?server_id=<sid>
  * POST /api/controlled-rewards/daily-weekly/claim?server_id=<sid>

SAFETY Pack 106:
  * Quadruple kill switch AND su ogni endpoint mutating:
      - REWARD_CLAIM_LEDGER_LIVE_ENABLED (global ledger)
      - MAIL_CLAIM_CONTROLLED_ENABLED / ACHIEVEMENT_CLAIM_CONTROLLED_ENABLED / DAILY_WEEKLY_REWARD_CLAIM_ENABLED (per-source)
  * Solo test marker `pack_106_test_artifact` accettato.
  * PSP obbligatorio. NO fallback `s1`.
  * idempotency_token mandatory (>=8 char).
  * Server-side claim_key deterministico.
  * Reward FISSO server-side dal catalog. Payload client IGNORATO.
  * Solo PSP `soft_currencies` + `materials` mutate. NO users.* mutation.
  * Achievement completion proof via marker test-only `pack_106_achievement_completion_<id>`.
  * Frontend guard `EXPO_PUBLIC_REWARD_CENTER_UI_ENABLED` + per-feature flags default OFF.
"""
import hashlib
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException, Depends
from pydantic import BaseModel

from data.controlled_reward_catalog_v1 import (
    CATALOG_VERSION as CONTROLLED_CATALOG_VERSION,
    get_mail_reward,
    get_achievement_reward,
    get_daily_weekly_task,
    list_catalog_summary,
)
from utils.reward_source_registry import (
    get_grant_fn,
    _PremiumGrantBlocked,
    _RewardTypeNotAllowed,
    ALLOWED_SOFT_CURRENCIES,
    FORBIDDEN_REWARD_TYPES,
)

PACK_106_USER_TEST_MARKER = "pack_106_test_artifact"
PACK_106_ACHIEVEMENT_COMPLETION_PREFIX = "pack_106_achievement_completion_"

GLOBAL_LEDGER_KILL_SWITCH_ENV = "REWARD_CLAIM_LEDGER_LIVE_ENABLED"
MAIL_KILL_SWITCH_ENV = "MAIL_CLAIM_CONTROLLED_ENABLED"
ACH_KILL_SWITCH_ENV = "ACHIEVEMENT_CLAIM_CONTROLLED_ENABLED"
DWR_KILL_SWITCH_ENV = "DAILY_WEEKLY_REWARD_CLAIM_ENABLED"

MAIL_CLAIM_SOURCE = "mail_claim_controlled"
ACH_CLAIM_SOURCE = "achievement_claim_controlled"
DWR_CLAIM_SOURCE = "daily_weekly_reward_claim"


def _truthy(v: Optional[str]) -> bool:
    return str(v or "false").strip().lower() in ("true", "1", "yes", "on")


def _global_ledger_on() -> bool: return _truthy(os.getenv(GLOBAL_LEDGER_KILL_SWITCH_ENV))
def _mail_on() -> bool: return _truthy(os.getenv(MAIL_KILL_SWITCH_ENV))
def _ach_on() -> bool: return _truthy(os.getenv(ACH_KILL_SWITCH_ENV))
def _dwr_on() -> bool: return _truthy(os.getenv(DWR_KILL_SWITCH_ENV))


async def _require_pack_106_test_user(db, uid: str) -> dict:
    user_doc = await db.users.find_one({"id": uid})
    if not user_doc or not user_doc.get(PACK_106_USER_TEST_MARKER):
        raise HTTPException(403, detail={
            "blocker": "CONTROLLED_REWARDS_ENDPOINT_TEST_ONLY",
            "marker_required": PACK_106_USER_TEST_MARKER,
        })
    return user_doc


async def _require_psp(db, uid: str, sid: str) -> Dict[str, Any]:
    psp = await db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})
    if not psp:
        raise HTTPException(409, detail={
            "blocker": "PLAYER_SERVER_PROFILE_REQUIRED",
            "server_id": sid,
        })
    return psp


def _validate_idempotency_token(t: Optional[str]) -> None:
    if not t or not isinstance(t, str) or len(t) < 8:
        raise HTTPException(400, detail={"blocker": "IDEMPOTENCY_TOKEN_REQUIRED"})


def _validate_server_id(sid: Optional[str]) -> str:
    if not sid or not isinstance(sid, str) or not sid.strip():
        raise HTTPException(400, detail={"blocker": "SERVER_ID_REQUIRED"})
    return sid.strip()


def _period_key(period: str) -> str:
    """UTC day for 'daily', UTC ISO week for 'weekly'."""
    now = datetime.now(timezone.utc)
    if period == "daily":
        return now.strftime("%Y-%m-%d")
    if period == "weekly":
        iso = now.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    raise HTTPException(500, detail={"blocker": "UNKNOWN_PERIOD", "period": period})


def _ensure_global_and(per_source_on: bool, per_source_blocker: str, per_source_env: str) -> None:
    if not _global_ledger_on():
        raise HTTPException(503, detail={
            "blocker": "REWARD_CLAIM_LEDGER_DISABLED",
            "kill_switch_env": GLOBAL_LEDGER_KILL_SWITCH_ENV,
        })
    if not per_source_on:
        raise HTTPException(503, detail={
            "blocker": per_source_blocker,
            "kill_switch_env": per_source_env,
        })


# ===== Pydantic models =====


class MailClaimRequest(BaseModel):
    mail_id: str
    idempotency_token: str


class AchievementClaimRequest(BaseModel):
    achievement_id: str
    idempotency_token: str


class DailyWeeklyClaimRequest(BaseModel):
    task_id: str
    idempotency_token: str


# ===== Registration =====


def register_controlled_rewards_routes(router, db, get_current_user, *_a, **_kw):

    @router.get("/controlled-rewards/health")
    async def cr_health():
        return {
            "endpoint_group": "/api/controlled-rewards",
            "pack_origin": "pack_106",
            "pack_106_test_marker": PACK_106_USER_TEST_MARKER,
            "kill_switches": {
                GLOBAL_LEDGER_KILL_SWITCH_ENV: _global_ledger_on(),
                MAIL_KILL_SWITCH_ENV: _mail_on(),
                ACH_KILL_SWITCH_ENV: _ach_on(),
                DWR_KILL_SWITCH_ENV: _dwr_on(),
            },
            "sources": {
                "mail_claim_controlled": "READY_GATED_RUNTIME_REQUIRED",
                "achievement_claim_controlled": "READY_GATED_COMPLETION_REQUIRED",
                "daily_weekly_reward_claim": "READY_GATED_RUNTIME_REQUIRED",
            },
            "controlled_catalog_version": CONTROLLED_CATALOG_VERSION,
            "reward_live_general": False,
            "premium_grants": False,
            "release_readiness_claimed": False,
            "no_users_gold_gems_experience_mutation": True,
            "no_account_wide_writes": True,
            "no_cross_server": True,
            "no_iap_gacha_payment": True,
            "no_battlepass_event_afk_pvp_guild_live": True,
            "_slc_pack_106_controlled_rewards_health": True,
        }

    @router.get("/controlled-rewards/catalog")
    async def cr_catalog():
        return {
            "catalog_version": CONTROLLED_CATALOG_VERSION,
            "content_identical_across_servers": True,
            **list_catalog_summary(),
            "reward_live_general": False,
            "release_readiness_claimed": False,
            "_slc_pack_106_controlled_catalog": True,
        }

    async def _grant_and_ledger(
        uid: str, sid: str, source: str, claim_key: str,
        idem_token_client: str, reward: Dict[str, Any], extra_ledger: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Helper: pre-check ledger + apply grant via grant_fn + insert ledger row."""
        existing = await db.reward_claim_ledger.find_one({
            "user_id": uid, "server_id": sid, "claim_source": source, "claim_key": claim_key,
        })
        if existing:
            existing.pop("_id", None)
            applied_at = existing.get("applied_at")
            if hasattr(applied_at, "isoformat"):
                applied_at = applied_at.isoformat()
            return {
                "idempotent_replay": True,
                "server_id": sid,
                "claim_source": source,
                "claim_key": claim_key,
                "rewards": existing.get("rewards"),
                "applied_at": applied_at,
                "reward_live_general": False,
                "premium_grant_blocked": True,
                f"_slc_pack_106_{source}_idempotent": True,
            }
        grant_fn = get_grant_fn(source)
        assert grant_fn is not None
        try:
            inc = grant_fn(db, uid, sid, {"_server_resolved_reward": reward})
        except _PremiumGrantBlocked as e:
            raise HTTPException(422, detail={"blocker": "PREMIUM_GRANT_BLOCKED", "key": str(e)})
        except _RewardTypeNotAllowed as e:
            raise HTTPException(422, detail={"blocker": "REWARD_TYPE_NOT_ALLOWED", "key": str(e)})
        if inc:
            await db.player_server_profiles.update_one(
                {"user_id": uid, "server_id": sid},
                {"$inc": inc}, upsert=False,
            )
        server_idem_token = hashlib.sha1(f"{claim_key}|{idem_token_client}".encode()).hexdigest()
        now = datetime.utcnow()
        rewards_summary = {
            "server_scoped_reward": reward,
            "applied_inc": {k: v for k, v in inc.items()},
        }
        ledger_row = {
            "user_id": uid, "server_id": sid,
            "claim_source": source, "claim_key": claim_key,
            "idempotency_token": server_idem_token,
            "client_idempotency_token_hash": hashlib.sha1(idem_token_client.encode()).hexdigest(),
            "rewards": rewards_summary,
            "applied_at": now, "created_at": now,
            f"_slc_pack_106_{source}": True,
            "_slc_pack_106_server_side_catalog": True,
            "_slc_pack_106_no_cross_server": True,
            **extra_ledger,
        }
        try:
            await db.reward_claim_ledger.insert_one(ledger_row)
        except Exception:
            # Rollback grant.
            if inc:
                rb = {k: -v for k, v in inc.items()}
                await db.player_server_profiles.update_one(
                    {"user_id": uid, "server_id": sid}, {"$inc": rb},
                )
            existing2 = await db.reward_claim_ledger.find_one({
                "user_id": uid, "server_id": sid,
                "claim_source": source, "claim_key": claim_key,
            })
            if existing2:
                existing2.pop("_id", None)
                ap = existing2.get("applied_at")
                if hasattr(ap, "isoformat"):
                    ap = ap.isoformat()
                return {
                    "idempotent_replay": True,
                    "server_id": sid, "claim_source": source, "claim_key": claim_key,
                    "rewards": existing2.get("rewards"),
                    "applied_at": ap,
                    "reward_live_general": False, "premium_grant_blocked": True,
                    f"_slc_pack_106_{source}_race_recovered": True,
                }
            raise HTTPException(500, detail={"blocker": "LEDGER_INSERT_FAILED"})
        return {
            "idempotent_replay": False,
            "server_id": sid,
            "claim_source": source,
            "claim_key": claim_key,
            "rewards": rewards_summary,
            "applied_at": now.isoformat(),
            "reward_live_general": False,
            "premium_grant_blocked": True,
            f"_slc_pack_106_{source}": True,
        }

    @router.post("/controlled-rewards/mail/claim")
    async def mail_claim(
        req: MailClaimRequest,
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        _ensure_global_and(_mail_on(), "MAIL_CLAIM_CONTROLLED_DISABLED", MAIL_KILL_SWITCH_ENV)
        sid = _validate_server_id(server_id)
        _validate_idempotency_token(req.idempotency_token)
        await _require_pack_106_test_user(db, uid)
        await _require_psp(db, uid, sid)
        mail = get_mail_reward(req.mail_id)
        if not mail:
            raise HTTPException(404, detail={
                "blocker": "MAIL_NOT_FOUND",
                "mail_id": req.mail_id,
            })
        claim_key = f"mail_{sid}_{req.mail_id}"
        return await _grant_and_ledger(
            uid, sid, MAIL_CLAIM_SOURCE, claim_key, req.idempotency_token,
            mail["reward"],
            {"mail_id": req.mail_id, "mail_title": mail["title"]},
        )

    @router.post("/controlled-rewards/achievement/claim")
    async def achievement_claim(
        req: AchievementClaimRequest,
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        _ensure_global_and(_ach_on(), "ACHIEVEMENT_CLAIM_CONTROLLED_DISABLED", ACH_KILL_SWITCH_ENV)
        sid = _validate_server_id(server_id)
        _validate_idempotency_token(req.idempotency_token)
        user_doc = await _require_pack_106_test_user(db, uid)
        await _require_psp(db, uid, sid)
        ach = get_achievement_reward(req.achievement_id)
        if not ach:
            raise HTTPException(404, detail={
                "blocker": "ACHIEVEMENT_NOT_FOUND",
                "achievement_id": req.achievement_id,
            })
        # Completion proof required: test-only marker on user doc.
        # Marker format: `pack_106_achievement_completion_<achievement_id>` = True.
        completion_marker = f"{PACK_106_ACHIEVEMENT_COMPLETION_PREFIX}{req.achievement_id}"
        if not user_doc.get(completion_marker):
            raise HTTPException(409, detail={
                "blocker": "ACHIEVEMENT_COMPLETION_REQUIRED",
                "achievement_id": req.achievement_id,
                "marker_required": completion_marker,
            })
        claim_key = f"achievement_{sid}_{req.achievement_id}"
        return await _grant_and_ledger(
            uid, sid, ACH_CLAIM_SOURCE, claim_key, req.idempotency_token,
            ach["reward"],
            {"achievement_id": req.achievement_id, "achievement_title": ach["title"]},
        )

    @router.post("/controlled-rewards/daily-weekly/claim")
    async def daily_weekly_claim(
        req: DailyWeeklyClaimRequest,
        server_id: str = None,
        current_user: dict = Depends(get_current_user),
    ):
        uid = current_user["id"]
        _ensure_global_and(_dwr_on(), "DAILY_WEEKLY_REWARD_CLAIM_DISABLED", DWR_KILL_SWITCH_ENV)
        sid = _validate_server_id(server_id)
        _validate_idempotency_token(req.idempotency_token)
        await _require_pack_106_test_user(db, uid)
        await _require_psp(db, uid, sid)
        task = get_daily_weekly_task(req.task_id)
        if not task:
            raise HTTPException(404, detail={
                "blocker": "TASK_NOT_FOUND",
                "task_id": req.task_id,
            })
        pkey = _period_key(task["period"])
        claim_key = f"dwr_{sid}_{req.task_id}_{pkey}"
        return await _grant_and_ledger(
            uid, sid, DWR_CLAIM_SOURCE, claim_key, req.idempotency_token,
            task["reward"],
            {"task_id": req.task_id, "period": task["period"], "period_key": pkey},
        )
