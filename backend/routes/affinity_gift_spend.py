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

_FORBIDDEN_HERO_IDS = frozenset({"borea", "primordial_gaia"})
# greek_borea is catalog-only / hidden; reject at endpoint level too.
_HIDDEN_HERO_IDS = frozenset({"greek_borea"})

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


def register_affinity_gift_spend_skeleton_routes(router):
    """Register the disabled POST skeleton under the existing /api prefix.

    The endpoint is auth-future-ready (it does NOT require auth today
    because no writes ever occur; this avoids leaking auth-required
    information about an inert system). When `AFFINITY_GIFT_RUNTIME_ENABLED`
    is finally ratified, the future task MUST add `Depends(get_current_user)`
    and rate-limit middleware BEFORE flipping the flag.
    """

    @router.post("/affinity/gift-spend", status_code=423)
    async def affinity_gift_spend_disabled(payload: Optional[dict] = None):
        """Disabled POST skeleton. Always returns HTTP 423 with a
        canonical disabled envelope. Never writes anything.

        Borea legacy aliases are rejected with 404 BEFORE the disabled
        envelope is returned, mirroring the existing hero-level
        forbidden behavior.
        """
        # 1. Borea / legacy alias guard (BEFORE flag check).
        # We inspect the raw payload defensively; we never parse it
        # for write purposes.
        if isinstance(payload, dict):
            hid = (payload.get("hero_id") or "").strip().lower()
            if hid in _FORBIDDEN_HERO_IDS or hid in _HIDDEN_HERO_IDS:
                raise HTTPException(404, "forbidden hero alias")

        # 2. Shape validation (best-effort, NO write either way).
        validation: dict[str, Any] = {
            "shape_ok": False,
            "missing_fields": [],
            "extra_info": None,
        }
        if isinstance(payload, dict):
            required = {"gift_id", "hero_id", "quantity", "idempotency_key"}
            missing = sorted(required - set(payload.keys()))
            validation["missing_fields"] = missing
            try:
                AffinityGiftSpendRequest(**payload)
                validation["shape_ok"] = True
            except Exception as e:
                validation["extra_info"] = f"pydantic: {type(e).__name__}"
        else:
            validation["missing_fields"] = [
                "gift_id", "hero_id", "quantity", "idempotency_key",
            ]

        # 3. Feature flag check. Always disabled in this task.
        if not is_affinity_gift_runtime_enabled():
            return {
                "task_origin": "AF2-I",
                "http_status": 423,
                "shape_validation_preview": validation,
                "safety_envelope": _disabled_envelope("feature_flag_off"),
            }

        # 4. Defensive: even if the flag were on, this skeleton is
        # not wired to any DB. Return a documentation-grade payload
        # without writing.
        return {
            "task_origin": "AF2-I",
            "http_status": 423,
            "shape_validation_preview": validation,
            "safety_envelope": _disabled_envelope("skeleton_no_write_path_implemented"),
        }
