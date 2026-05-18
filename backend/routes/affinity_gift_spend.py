"""
AF2-G — Affinity Gift Spend POST Skeleton (DISABLED / NO-WRITE)
─────────────────────────────────────────────────────────────────────
Auth-gated POST /api/affinity/gift-spend endpoint skeleton that is
HARD-DISABLED by the `AFFINITY_GIFT_RUNTIME_ENABLED` feature flag.

ABSOLUTE RULES:
  - Only env value EXACTLY `true_explicit_affinity_gift_runtime_on`
    is recognized as truthy. The task MUST NOT set it.
  - When disabled (default), the endpoint always returns HTTP 423
    (Locked) with a canonical disabled envelope. No DB connection
    opened. No inventory mutation. No affinity points mutation.
  - Borea legacy aliases (`borea`, `primordial_gaia`) are rejected
    with HTTP 404 BEFORE any other check, to mirror the existing
    hero-level forbidden behavior.
  - The handler validates only the SHAPE of the payload (gift_id,
    hero_id, quantity, idempotency_key) but NEVER writes.
"""
from __future__ import annotations
import os
from typing import Any, Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field


_ENV_VAR = "AFFINITY_GIFT_RUNTIME_ENABLED"
_TRUTHY_ALLOWLIST = frozenset({"true_explicit_affinity_gift_runtime_on"})

# AF2-N canary: only user_ids listed here may spend even when the
# runtime flag is on. Empty / unset = nobody can spend (still 423).
_CANARY_ALLOWLIST_ENV = "AFFINITY_GIFT_CANARY_ALLOWLIST"
# AF2-N safety cap: max rows the runtime will ever allow during canary.
# Beyond this, even allowlist users are short-circuited to 423.
_CANARY_LEDGER_CAP_ENV = "AFFINITY_GIFT_CANARY_LEDGER_CAP"
_CANARY_LEDGER_CAP_DEFAULT = 50

# AF2-N V16 \u2014 dedicated flag for inventory live writes (Stage1 only).
_INVENTORY_WRITES_ENV = "AFFINITY_GIFT_INVENTORY_WRITES_ENABLED"
_INVENTORY_WRITES_ON_VALUE = "true_explicit_affinity_inventory_on"


def _inventory_writes_enabled() -> bool:
    """V16: true only when the dedicated env flag is set to the explicit value."""
    return os.environ.get(_INVENTORY_WRITES_ENV, "") == _INVENTORY_WRITES_ON_VALUE

_FORBIDDEN_HERO_IDS = frozenset({"borea", "primordial_gaia"})
# greek_borea is catalog-only / hidden; reject at endpoint level too.
_HIDDEN_HERO_IDS = frozenset({"greek_borea"})

# V21 — Rate-limit guard (in-memory sliding window). Minimal, fail-open on
# any internal error to never break existing safe behavior. Borea check
# ALWAYS runs first, so 404 wins over 429. Non-allowlist still gets 423
# unless velocity threshold exceeded — then 429 (does NOT write DB).
_RATE_LIMIT_ENV = "AFFINITY_GIFT_RATE_LIMIT_ENABLED"
_RATE_LIMIT_ON_VALUE = "true_explicit_affinity_rate_limit_on"
_RL_PER_USER_PER_MIN = 30
_RL_PER_USER_PER_HOUR = 240
_RL_PER_IP_PER_MIN = 60
_RL_BURST_WINDOW_S = 10
_RL_BURST_MAX = 6
# event log: {(scope, key): [epoch_seconds, ...]}
_RL_EVENTS: dict = {}


def _rate_limit_enabled() -> bool:
    return os.environ.get(_RATE_LIMIT_ENV, "") == _RATE_LIMIT_ON_VALUE


def _rl_record(scope: str, key: str) -> None:
    import time
    now = time.time()
    ev = _RL_EVENTS.setdefault((scope, key), [])
    ev.append(now)
    if len(ev) > 1000:
        cutoff = now - 3600
        _RL_EVENTS[(scope, key)] = [t for t in ev if t >= cutoff]


def _rl_count(scope: str, key: str, window_s: float) -> int:
    import time
    now = time.time()
    cutoff = now - window_s
    ev = _RL_EVENTS.get((scope, key), [])
    return sum(1 for t in ev if t >= cutoff)


def _rate_limit_check(user_id: str, client_ip: str):
    """Return (allowed, reason, snapshot). Allowed=False means breach.

    Records the request only if allowed (a 429 should NOT count toward the
    quota since no actual work is done).
    """
    if not _rate_limit_enabled():
        return True, None, {"rate_limit_enabled": False}
    uid = (user_id or "<anon>").strip() or "<anon>"
    ip = (client_ip or "<noip>").strip() or "<noip>"
    user_burst = _rl_count("user", uid, _RL_BURST_WINDOW_S)
    user_min = _rl_count("user", uid, 60)
    user_hour = _rl_count("user", uid, 3600)
    ip_min = _rl_count("ip", ip, 60)
    snapshot = {
        "rate_limit_enabled": True,
        "user_burst": user_burst, "burst_max": _RL_BURST_MAX,
        "user_min": user_min, "user_min_max": _RL_PER_USER_PER_MIN,
        "user_hour": user_hour, "user_hour_max": _RL_PER_USER_PER_HOUR,
        "ip_min": ip_min, "ip_min_max": _RL_PER_IP_PER_MIN,
    }
    if user_burst >= _RL_BURST_MAX:
        return False, "user_burst_exceeded", snapshot
    if user_min >= _RL_PER_USER_PER_MIN:
        return False, "user_per_minute_exceeded", snapshot
    if user_hour >= _RL_PER_USER_PER_HOUR:
        return False, "user_per_hour_exceeded", snapshot
    if ip_min >= _RL_PER_IP_PER_MIN:
        return False, "ip_per_minute_exceeded", snapshot
    _rl_record("user", uid)
    _rl_record("ip", ip)
    snapshot["user_burst"] = user_burst + 1
    snapshot["user_min"] = user_min + 1
    snapshot["user_hour"] = user_hour + 1
    snapshot["ip_min"] = ip_min + 1
    return True, None, snapshot


# AF2-H — future-runtime hardening metadata. These constants ONLY
# document the auth / rate-limit / idempotency contract that a future
# task (post AFFINITY_GIFT_RUNTIME_ENABLED flip) MUST satisfy. Today
# they are not enforced (the endpoint is hard-disabled) and they MUST
# NOT trigger any side effect / DB write / external call.
AUTH_REQUIRED_FUTURE: bool = True
AUTH_STRATEGY_FUTURE: str = "Depends(get_current_user)"
RATE_LIMIT_REQUIRED_FUTURE: bool = True
RATE_LIMIT_PER_USER_PER_MINUTE_FUTURE: int = 30
RATE_LIMIT_PER_USER_PER_HOUR_FUTURE: int = 240
RATE_LIMIT_PER_IP_PER_MINUTE_FUTURE: int = 60
RATE_LIMIT_BURST_WINDOW_SECONDS_FUTURE: int = 10
RATE_LIMIT_BURST_MAX_FUTURE: int = 6
IDEMPOTENCY_REQUIRED_FUTURE: bool = True
IDEMPOTENCY_KEY_HEADER_FUTURE: str = "Idempotency-Key"
IDEMPOTENCY_WINDOW_HOURS_FUTURE: int = 24
IDEMPOTENCY_KEY_MIN_LEN: int = 8
IDEMPOTENCY_KEY_MAX_LEN: int = 128
REPLAY_PROTECTION_STRATEGY_FUTURE: str = (
    "store idempotency_key in gift_transaction_ledger with unique index; "
    "duplicates return HTTP 409 with same response payload"
)
TRANSACTION_INTEGRITY_REQUIRED_FUTURE: bool = True
TRANSACTION_STRATEGY_FUTURE: str = (
    "MongoDB multi-document transaction across user_gift_inventory + "
    "gift_transaction_ledger + hero_affinity_state"
)
BOREA_VISIBILITY_GATE_REQUIRED_FUTURE: bool = True


def _af2i_concrete_contract() -> dict[str, Any]:
    """AF2-I — concrete auth / rate-limit / idempotency CONTRACT for
    the gift-spend endpoint.

    Unlike `_hardening_metadata()` (AF2-H, which describes only the
    FUTURE state), this block formalizes the **current contract** that
    the endpoint binds to, even while it stays disabled / no-write.

    Today the contract is NOT enforced in code (we deliberately keep
    the inert skeleton no-write to avoid leaking auth-required signals
    on an inert system), but every flag below is a precondition that a
    future runtime-flip task MUST honor. The contract is the
    canonical reference for auditors.
    """
    return {
        "contract_id": "affinity_gift_spend_disabled_contract_v2",
        "task_origin": "AF2-I",
        "auth_required": True,
        "auth_enforced_when_runtime_enabled": True,
        "rate_limit_policy_ref": "affinity_gift_anti_exploit_policy_v1",
        "rate_limits": {
            "per_user_per_minute": RATE_LIMIT_PER_USER_PER_MINUTE_FUTURE,
            "per_user_per_hour": RATE_LIMIT_PER_USER_PER_HOUR_FUTURE,
            "per_ip_per_minute": RATE_LIMIT_PER_IP_PER_MINUTE_FUTURE,
            "burst_window_seconds": RATE_LIMIT_BURST_WINDOW_SECONDS_FUTURE,
            "burst_max": RATE_LIMIT_BURST_MAX_FUTURE,
        },
        "idempotency_key_required": True,
        "idempotency_key_header": IDEMPOTENCY_KEY_HEADER_FUTURE,
        "idempotency_window_hours": IDEMPOTENCY_WINDOW_HOURS_FUTURE,
        "idempotency_key_min_len": IDEMPOTENCY_KEY_MIN_LEN,
        "idempotency_key_max_len": IDEMPOTENCY_KEY_MAX_LEN,
        "replay_protection_required": True,
        "replay_protection_strategy_ref": (
            "store idempotency_key in gift_transaction_ledger with unique "
            "index; duplicates return HTTP 409 with the original payload"
        ),
        "no_write_current_task": True,
        "borea_visibility_gate_required": True,
        "hidden_aliases_blocked": sorted(_FORBIDDEN_HERO_IDS | _HIDDEN_HERO_IDS),
        "currently_enforced_today": False,
        "currently_enforced_today_rationale": (
            "Endpoint is hard-disabled (HTTP 423); enforcement would only "
            "leak signal about inert state. Contract becomes ENFORCED the "
            "moment AFFINITY_GIFT_RUNTIME_ENABLED is flipped."
        ),
    }


def _hardening_metadata() -> dict[str, Any]:
    """Return the AF2-H hardening metadata for the disabled envelope.

    All values describe FUTURE requirements only. The endpoint stays
    disabled / no-write today and MUST NOT enforce these checks until
    AFFINITY_GIFT_RUNTIME_ENABLED is flipped under a controlled task.
    """
    return {
        "auth_required_future": AUTH_REQUIRED_FUTURE,
        "auth_strategy_future": AUTH_STRATEGY_FUTURE,
        "rate_limit_required_future": RATE_LIMIT_REQUIRED_FUTURE,
        "rate_limit_per_user_per_minute_future": RATE_LIMIT_PER_USER_PER_MINUTE_FUTURE,
        "rate_limit_per_user_per_hour_future": RATE_LIMIT_PER_USER_PER_HOUR_FUTURE,
        "rate_limit_per_ip_per_minute_future": RATE_LIMIT_PER_IP_PER_MINUTE_FUTURE,
        "rate_limit_burst_window_seconds_future": RATE_LIMIT_BURST_WINDOW_SECONDS_FUTURE,
        "rate_limit_burst_max_future": RATE_LIMIT_BURST_MAX_FUTURE,
        "idempotency_required_future": IDEMPOTENCY_REQUIRED_FUTURE,
        "idempotency_key_header_future": IDEMPOTENCY_KEY_HEADER_FUTURE,
        "idempotency_window_hours_future": IDEMPOTENCY_WINDOW_HOURS_FUTURE,
        "idempotency_key_min_len": IDEMPOTENCY_KEY_MIN_LEN,
        "idempotency_key_max_len": IDEMPOTENCY_KEY_MAX_LEN,
        "replay_protection_strategy_future": REPLAY_PROTECTION_STRATEGY_FUTURE,
        "transaction_integrity_required_future": TRANSACTION_INTEGRITY_REQUIRED_FUTURE,
        "transaction_strategy_future": TRANSACTION_STRATEGY_FUTURE,
        "borea_visibility_gate_required_future": BOREA_VISIBILITY_GATE_REQUIRED_FUTURE,
        "currently_enforced": False,
        "rationale_for_not_enforcing_today": (
            "Endpoint is hard-disabled (HTTP 423) and writes are physically "
            "impossible; auth / rate-limit / idempotency checks would leak "
            "information about an inert system. Enforcement will be added "
            "by AF2-I BEFORE flipping AFFINITY_GIFT_RUNTIME_ENABLED."
        ),
    }


def is_affinity_gift_runtime_enabled() -> bool:
    """Return True only if env var EXACTLY equals the allowlisted token."""
    return os.environ.get(_ENV_VAR, "") in _TRUTHY_ALLOWLIST


def _disabled_envelope(reason: str) -> dict[str, Any]:
    return {
        "enabled": False,
        "runtime_attached": False,
        "applied_to_combat": False,
        "db_write": False,
        "inventory_write": False,
        "affinity_points_write": False,
        "stat_buffs_enabled": False,
        "gift_spend_executed": False,
        "idempotency_required": True,
        "no_borea_activation": True,
        "feature_flag": _ENV_VAR,
        "feature_flag_currently_enabled": bool(is_affinity_gift_runtime_enabled()),
        "reason": reason,
        "hidden_aliases_blocked": sorted(_FORBIDDEN_HERO_IDS | _HIDDEN_HERO_IDS),
        # AF2-H — future-runtime hardening metadata (documentation only,
        # never enforced today; the endpoint is hard-disabled).
        "future_runtime_hardening": _hardening_metadata(),
        # AF2-I — concrete contract bound to this endpoint. Not enforced
        # while feature_flag_currently_enabled=False, but it IS the
        # canonical contract that the future runtime task must honor.
        "af2i_concrete_contract": _af2i_concrete_contract(),
    }


class AffinityGiftSpendRequest(BaseModel):
    gift_id: str = Field(..., min_length=1, max_length=128)
    hero_id: str = Field(..., min_length=1, max_length=128)
    quantity: int = Field(default=1, ge=1, le=999)
    idempotency_key: str = Field(..., min_length=8, max_length=128)


def _canary_allowlist() -> frozenset[str]:
    """AF2-N canary allowlist (user_ids), parsed from env var.

    Returns an empty frozenset when unset or empty -> no user is in the
    canary, meaning even with the runtime flag on, requests get 423.
    """
    raw = os.environ.get(_CANARY_ALLOWLIST_ENV, "")
    return frozenset(s.strip() for s in raw.split(",") if s.strip())


def _canary_ledger_cap() -> int:
    """AF2-N hard cap on the total rows the canary can ever insert.

    V18: hard upper bound raised to 5000 to accommodate Stage3 QA expansion
    (env-configured cap, e.g. 2500). The 5000 ceiling is a non-negotiable
    safety cap; values above are clamped down.
    """
    try:
        v = int(os.environ.get(_CANARY_LEDGER_CAP_ENV, ""))
    except Exception:
        v = _CANARY_LEDGER_CAP_DEFAULT
    if v <= 0:
        v = _CANARY_LEDGER_CAP_DEFAULT
    return min(v, 5000)


def register_affinity_gift_spend_skeleton_routes(router):
    """Register the gift-spend POST endpoint under the existing /api prefix.

    Three states:

    1. Runtime DISABLED (default) -> always returns HTTP 423 with a
       canonical disabled envelope. No DB connection opened. No
       inventory mutation. No affinity points mutation.
    2. Runtime ENABLED but caller `user_id` NOT in the canary allowlist
       -> returns HTTP 423 with `disabled_reason=not_in_canary_allowlist`.
    3. Runtime ENABLED AND caller `user_id` IS in the canary allowlist
       AND ledger row count < hard cap -> performs a controlled ledger
       insert (idempotency-checked) and returns HTTP 200. NO inventory
       mutation. NO affinity points mutation. NO buff activation. NO
       battle wiring. Borea aliases ALWAYS return 404 BEFORE any state
       transition.
    """

    from fastapi import Request as _FastApiRequest

    @router.post("/affinity/gift-spend")
    async def affinity_gift_spend_disabled(payload: Optional[dict] = None, request: _FastApiRequest = None):
        """Affinity gift-spend endpoint, AF2-N canary aware + V21 rate-limit."""
        from fastapi.responses import JSONResponse

        # 1. Borea / legacy alias guard (BEFORE flag/rate-limit check).
        if isinstance(payload, dict):
            hid = (payload.get("hero_id") or "").strip().lower()
            if hid in _FORBIDDEN_HERO_IDS or hid in _HIDDEN_HERO_IDS:
                raise HTTPException(404, "forbidden hero alias")

        # 1.5 V21 rate-limit guard. Borea 404 already won. Non-DB-touching.
        try:
            user_id_for_rl = ""
            if isinstance(payload, dict):
                user_id_for_rl = str(payload.get("user_id") or "").strip()
            client_ip = ""
            if request is not None:
                try:
                    client_ip = (request.client.host if request.client else "") or ""
                except Exception:
                    client_ip = ""
            rl_ok, rl_reason, rl_snap = _rate_limit_check(user_id_for_rl, client_ip)
            if not rl_ok:
                return JSONResponse(
                    status_code=429,
                    content={
                        "task_origin": "AF2-N-V21-RATE-LIMIT",
                        "http_status": 429,
                        "disabled_reason": rl_reason,
                        "rate_limit_snapshot": rl_snap,
                        "db_write": False,
                        "safety_envelope": _disabled_envelope(f"rate_limited:{rl_reason}"),
                    },
                )
        except Exception:
            # fail-open on rate-limit internal errors (never block runtime path)
            pass


        # 2. Shape validation (best-effort).
        validation: dict[str, Any] = {
            "shape_ok": False, "missing_fields": [], "extra_info": None,
        }
        validated = None
        if isinstance(payload, dict):
            required = {"gift_id", "hero_id", "quantity", "idempotency_key"}
            missing = sorted(required - set(payload.keys()))
            validation["missing_fields"] = missing
            try:
                validated = AffinityGiftSpendRequest(**payload)
                validation["shape_ok"] = True
            except Exception as e:
                validation["extra_info"] = f"pydantic: {type(e).__name__}"
        else:
            validation["missing_fields"] = [
                "gift_id", "hero_id", "quantity", "idempotency_key",
            ]

        # 3. Feature flag gate.
        if not is_affinity_gift_runtime_enabled():
            return JSONResponse(
                status_code=423,
                content={
                    "task_origin": "AF2-I",
                    "http_status": 423,
                    "shape_validation_preview": validation,
                    "safety_envelope": _disabled_envelope("feature_flag_off"),
                },
            )

        # 4. AF2-N canary: allowlist + ledger cap gate.
        allowlist = _canary_allowlist()
        user_id = ""
        if isinstance(payload, dict):
            user_id = str(payload.get("user_id") or "").strip()

        if not allowlist or user_id not in allowlist:
            return JSONResponse(
                status_code=423,
                content={
                    "task_origin": "AF2-N",
                    "http_status": 423,
                    "shape_validation_preview": validation,
                    "disabled_reason": "not_in_canary_allowlist",
                    "safety_envelope": _disabled_envelope("not_in_canary_allowlist"),
                },
            )

        if not validation.get("shape_ok") or validated is None:
            raise HTTPException(400, "invalid payload shape")

        # 5. AF2-N canary execution: idempotency-check + controlled
        # ledger insert. NO inventory mutation. NO affinity points
        # mutation. NO buff. NO battle wiring.
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
            db_name = os.environ.get("DB_NAME", "divine_waifus")
            client = AsyncIOMotorClient(mongo_url)
            db = client[db_name]
            coll = db["gift_transaction_ledger"]

            # Idempotency check (replay protection)
            existing = await coll.find_one({
                "user_id": user_id,
                "idempotency_key": validated.idempotency_key,
            })
            if existing:
                return JSONResponse(
                    status_code=200,
                    content={
                        "task_origin": "AF2-N",
                        "http_status": 200,
                        "result": "idempotent_replay",
                        "tx_id": existing.get("tx_id"),
                        "ledger_row_inserted": False,
                        "safety_envelope": _canary_envelope(),
                    },
                )

            # Hard cap check
            current_rows = await coll.count_documents({})
            cap = _canary_ledger_cap()
            if current_rows >= cap:
                return JSONResponse(
                    status_code=423,
                    content={
                        "task_origin": "AF2-N",
                        "http_status": 423,
                        "disabled_reason": "canary_ledger_cap_reached",
                        "canary_ledger_cap": cap,
                        "canary_ledger_rows": current_rows,
                        "safety_envelope": _disabled_envelope("canary_ledger_cap_reached"),
                    },
                )

            from datetime import datetime, timezone
            import uuid
            tx_id = f"tx_canary_{uuid.uuid4().hex[:16]}"

            # V16: inventory-live path. Active only when dedicated flag is on
            # AND user is in allowlist AND hero is not Borea (already filtered
            # above). Pre-check inventory BEFORE any write to keep atomicity.
            hid = validated.hero_id.strip().lower()
            inventory_writes_on = _inventory_writes_enabled()
            inv_live_for_this_request = (inventory_writes_on
                                          and user_id in (allowlist or set())
                                          and hid not in _FORBIDDEN_HERO_IDS
                                          and hid not in _HIDDEN_HERO_IDS)
            inv_doc = None
            if inv_live_for_this_request:
                ugi = db["user_gift_inventory"]
                inv_doc = await ugi.find_one({"user_id": user_id, "gift_id": validated.gift_id})
                if (not inv_doc) or inv_doc.get("quantity", 0) < validated.quantity:
                    return JSONResponse(
                        status_code=412,
                        content={
                            "task_origin": "AF2-N-INV-LIVE",
                            "http_status": 412,
                            "result": "inventory_insufficient",
                            "available": (inv_doc or {}).get("quantity", 0),
                            "requested": validated.quantity,
                            "safety_envelope": _disabled_envelope("inventory_insufficient"),
                        },
                    )

            doc = {
                "tx_id": tx_id,
                "transaction_id": tx_id,  # matches schema's idx_tx_id_unique
                "user_id": user_id,
                "gift_id": validated.gift_id,
                "hero_id": hid,
                "quantity": validated.quantity,
                "idempotency_key": validated.idempotency_key,
                "status": "applied_inventory_live" if inv_live_for_this_request else "applied_canary",
                "created_at_utc": datetime.now(timezone.utc),
                "canary": True,
                "task_origin": "AF2-N-INV-LIVE" if inv_live_for_this_request else "AF2-N",
                "inventory_mutated": bool(inv_live_for_this_request),
                "affinity_points_mutated": bool(inv_live_for_this_request),
                "buffs_activated": False,
                "battle_wiring_attached": False,
            }
            await coll.insert_one(doc)

            # V16: execute inventory + affinity_state mutations (sequentially
            # but with strict guards). If inventory decrement fails (race),
            # the ledger row is reversed by delete_one to keep state consistent.
            inventory_after = None
            affinity_points_after = None
            if inv_live_for_this_request:
                ugi = db["user_gift_inventory"]
                uas = db["user_affinity_state"]
                now = datetime.now(timezone.utc)
                dec_res = await ugi.update_one(
                    {"user_id": user_id, "gift_id": validated.gift_id,
                     "quantity": {"$gte": validated.quantity}},
                    {"$inc": {"quantity": -validated.quantity},
                     "$set": {"updated_at": now, "last_tx_id": tx_id}},
                )
                if dec_res.matched_count != 1:
                    # Race lost. Reverse ledger row.
                    await coll.delete_one({"tx_id": tx_id})
                    return JSONResponse(
                        status_code=412,
                        content={
                            "task_origin": "AF2-N-INV-LIVE",
                            "http_status": 412,
                            "result": "inventory_race_lost_rolled_back",
                            "safety_envelope": _disabled_envelope("inventory_race_lost"),
                        },
                    )
                pts_delta = 1 * validated.quantity  # 1 affinity point / unit (V16 default)
                await uas.update_one(
                    {"user_id": user_id, "hero_id": hid},
                    {"$inc": {"affinity_points": pts_delta,
                              "total_gifts_given": validated.quantity},
                     "$set": {"updated_at": now,
                              "last_gift_id": validated.gift_id,
                              "last_tx_id": tx_id},
                     "$setOnInsert": {"created_at": now,
                                       "affinity_tier": 0,
                                       "metadata": {"seed_task": "V16_live_write",
                                                    "is_qa_user": True}}},
                    upsert=True,
                )
                inv_after_doc = await ugi.find_one(
                    {"user_id": user_id, "gift_id": validated.gift_id},
                    projection={"_id": 0, "quantity": 1})
                inventory_after = (inv_after_doc or {}).get("quantity")
                uas_doc = await uas.find_one(
                    {"user_id": user_id, "hero_id": hid},
                    projection={"_id": 0, "affinity_points": 1})
                affinity_points_after = (uas_doc or {}).get("affinity_points")

            return JSONResponse(
                status_code=200,
                content={
                    "task_origin": "AF2-N-INV-LIVE" if inv_live_for_this_request else "AF2-N",
                    "http_status": 200,
                    "result": "applied_inventory_live" if inv_live_for_this_request else "applied_canary",
                    "tx_id": tx_id,
                    "ledger_row_inserted": True,
                    "ledger_rows_after_insert": current_rows + 1,
                    "canary_ledger_cap": cap,
                    "inventory_mutated": bool(inv_live_for_this_request),
                    "affinity_points_mutated": bool(inv_live_for_this_request),
                    "inventory_after": inventory_after,
                    "affinity_points_after": affinity_points_after,
                    "safety_envelope": _canary_envelope(),
                },
            )
        except HTTPException:
            raise
        except Exception as e:
            # On any unexpected error, fail closed (423) and NEVER expose
            # internal state. NO partial writes survive because the only
            # write op is insert_one which is atomic.
            return JSONResponse(
                status_code=423,
                content={
                    "task_origin": "AF2-N",
                    "http_status": 423,
                    "disabled_reason": f"canary_fail_closed: {type(e).__name__}",
                    "safety_envelope": _disabled_envelope("canary_fail_closed"),
                },
            )

    # AF2-N-READINESS-DASH (read-only status endpoint).
    @router.get("/affinity/gift-spend/canary-status")
    async def affinity_gift_spend_canary_status():
        """Read-only canary status snapshot. No DB write."""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
            db_name = os.environ.get("DB_NAME", "divine_waifus")
            client = AsyncIOMotorClient(mongo_url)
            coll = client[db_name]["gift_transaction_ledger"]
            total_rows = await coll.count_documents({})
            canary_rows = await coll.count_documents({"canary": True})
            last_doc = await coll.find_one(
                {"canary": True}, sort=[("created_at_utc", -1)],
                projection={"_id": 0, "tx_id": 1, "user_id": 1,
                            "gift_id": 1, "hero_id": 1, "quantity": 1,
                            "status": 1, "created_at_utc": 1}
            )
            if last_doc and 'created_at_utc' in last_doc:
                last_doc['created_at_utc'] = str(last_doc['created_at_utc'])
        except Exception as e:
            total_rows = -1; canary_rows = -1; last_doc = None
        runtime_on = is_affinity_gift_runtime_enabled()
        allowlist = _canary_allowlist()
        return {
            "task_origin": "AF2-N-READINESS-DASH",
            "design_only": False,
            "runtime_attached": runtime_on,
            "db_write": False,  # this endpoint is read-only
            "feature_flag": _ENV_VAR,
            "feature_flag_currently_enabled": runtime_on,
            "canary_allowlist_size": len(allowlist),
            "canary_ledger_cap": _canary_ledger_cap(),
            "ledger_total_rows": total_rows,
            "ledger_canary_rows": canary_rows,
            "last_canary_tx": last_doc,
            "borea_aliases_blocked": ["borea", "greek_borea", "primordial_gaia"],
            "applied_to_combat": False,
            "battle_runtime_attached": False,
            "inventory_mutation_enabled": _inventory_writes_enabled(),
            "affinity_points_mutation_enabled": _inventory_writes_enabled(),
            "buffs_enabled": False,
            "inventory_writes_flag_dependency": _INVENTORY_WRITES_ENV,
            "rate_limit_enabled": _rate_limit_enabled(),
            "rate_limit_per_user_per_minute": _RL_PER_USER_PER_MIN,
            "rate_limit_per_user_per_hour": _RL_PER_USER_PER_HOUR,
            "rate_limit_per_ip_per_minute": _RL_PER_IP_PER_MIN,
            "rate_limit_burst_window_seconds": _RL_BURST_WINDOW_S,
            "rate_limit_burst_max": _RL_BURST_MAX,
            "rate_limit_flag_dependency": _RATE_LIMIT_ENV,
        }


def _canary_envelope() -> dict[str, Any]:
    """AF2-N canary safety envelope (sanitized; no PII)."""
    inv_on = _inventory_writes_enabled()
    return {
        "mode": "inventory_live_stage1" if inv_on else "canary",
        "runtime_attached": True,
        "battle_runtime_attached": False,
        "applied_to_combat": False,
        "db_write": True,
        "db_write_scope": (
            "gift_transaction_ledger + user_gift_inventory + user_affinity_state (Stage1 allowlist only)"
            if inv_on else
            "gift_transaction_ledger only (no inventory, no affinity_points)"
        ),
        "inventory_mutated": inv_on,
        "affinity_points_mutated": inv_on,
        "buffs_activated": False,
        "borea_activation": False,
        "feature_flag_dependency": _ENV_VAR,
        "feature_flag_currently_enabled": True,
        "canary_allowlist_active": True,
        "hidden_aliases_blocked": ["borea", "greek_borea", "primordial_gaia"],
        "inventory_writes_flag_dependency": _INVENTORY_WRITES_ENV,
        "inventory_writes_flag_currently_enabled": inv_on,
    }
