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
                "task_origin": "AF2-G",
                "http_status": 423,
                "shape_validation_preview": validation,
                "safety_envelope": _disabled_envelope("feature_flag_off"),
            }

        # 4. Defensive: even if the flag were on, this skeleton is
        # not wired to any DB. Return a documentation-grade payload
        # without writing.
        return {
            "task_origin": "AF2-G",
            "http_status": 423,
            "shape_validation_preview": validation,
            "safety_envelope": _disabled_envelope("skeleton_no_write_path_implemented"),
        }
