"""AF2-N-INVENTORY-WIRING-PRE — Inert inventory preview adapter.

This module is the preview/contract for a FUTURE inventory wiring task.
It is NOT imported by any live route, by battle_engine/battle_core, or
by UI files. The entry point `preview_inventory_apply` always returns
`runtime_attached=False` and performs NO DB writes, NO inventory
mutation, NO affinity_points mutation.

Absolute rules (enforced by audit):
  - No top-level import of `battle_engine`, `battle_core`, or any
    frontend module.
  - No motor/pymongo write call.
  - No insert_one / update_one / delete_one in this file.
  - Always returns `runtime_attached=False`.
  - Borea hero_ids set `borea_filtered=True` and abort the preview.
"""
from __future__ import annotations
import os
from typing import Any

_FORBIDDEN_HERO_IDS = frozenset({"borea", "greek_borea", "primordial_gaia"})
_FEATURE_FLAG_NAME = "AFFINITY_GIFT_INVENTORY_WIRING_ENABLED"


def _feature_flag_enabled() -> bool:
    """Always returns False until a future explicit task enables it."""
    return os.environ.get(_FEATURE_FLAG_NAME, "") == "true_explicit_inventory_wiring_on"


def _safety_envelope() -> dict[str, Any]:
    return {
        "preview_only": True,
        "design_only": True,
        "runtime_attached": False,
        "inventory_mutation_attempted": False,
        "inventory_mutation_committed": False,
        "affinity_points_mutation_attempted": False,
        "affinity_points_mutation_committed": False,
        "db_write": False,
        "feature_flag_dependency": _FEATURE_FLAG_NAME,
        "feature_flag_currently_enabled": _feature_flag_enabled(),
        "hidden_aliases_blocked": sorted(_FORBIDDEN_HERO_IDS),
    }


def preview_inventory_apply(
    user_id: str,
    gift_id: str,
    hero_id: str,
    quantity: int,
    affinity_points_delta: int = 0,
) -> dict[str, Any]:
    """Pure preview. Returns the shape the future write path would have.

    This function NEVER mutates DB state. It documents the schema and
    invariants the future implementation MUST honor (including the
    Borea filter).
    """
    hid = (hero_id or "").strip().lower()
    uid = (user_id or "").strip()
    qty = max(0, int(quantity)) if isinstance(quantity, (int, float)) else 0
    pts = int(affinity_points_delta) if isinstance(affinity_points_delta, (int, float)) else 0

    borea_filtered = hid in _FORBIDDEN_HERO_IDS
    if borea_filtered:
        return {
            "task_origin": "AF2-N-INVENTORY-WIRING-PRE",
            "preview_version": "v1",
            "user_id": uid, "hero_id": hid, "gift_id": (gift_id or "").strip(),
            "runtime_attached": False,
            "would_have_consumed_inventory": False,
            "would_have_credited_points": False,
            "would_have_status": "borea_filtered",
            "borea_filtered": True,
            "safety_envelope": _safety_envelope(),
        }

    # In the future runtime, the following would happen ATOMICALLY:
    #   inventory[gift_id] -= qty (must remain >= 0; else reject)
    #   affinity_points[hero_id] += pts (capped per economy policy)
    # Today we ONLY return the shape; we do NOTHING.
    return {
        "task_origin": "AF2-N-INVENTORY-WIRING-PRE",
        "preview_version": "v1",
        "user_id": uid, "hero_id": hid, "gift_id": (gift_id or "").strip(),
        "quantity": qty, "affinity_points_delta": pts,
        "runtime_attached": False,
        "would_have_consumed_inventory": qty > 0,
        "would_have_credited_points": pts != 0,
        "would_have_status": "applied_preview_only",
        "borea_filtered": False,
        "atomicity_contract": "single-document transaction in future task; pre-check inventory >= qty BEFORE any mutation",
        "caps_contract": "affinity_points capped per affinity_phase2_economy_cap_policy_draft_v1",
        "safety_envelope": _safety_envelope(),
    }


__all__ = ["preview_inventory_apply"]
