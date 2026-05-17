"""AF2-N-INVENTORY-WIRING-SHADOW — Shadow / dry-run inventory adapter.

INERT MODULE. Extends the V13 inventory_wiring_preview_adapter contract with
rollback / compensation semantics, BUT still writes nothing. Returns a
detailed dry-run record describing what a future live wiring WOULD do.

Absolute rules (enforced by audit):
  - No top-level import of `battle_engine`, `battle_core`, or any frontend module.
  - No motor/pymongo import.
  - No DB write method call sites (insert_one / update_one / delete_one).
  - Always returns `runtime_attached=False` and `db_write=False`.
  - Borea hero_ids -> `borea_filtered=True`, dry-run aborts.
"""
from __future__ import annotations
import os
from typing import Any

_FORBIDDEN_HERO_IDS = frozenset({'borea', 'greek_borea', 'primordial_gaia'})
_FEATURE_FLAG_NAME = 'AFFINITY_GIFT_INVENTORY_WIRING_ENABLED'
_AFFINITY_POINTS_FLAG = 'AFFINITY_POINTS_MUTATION_ENABLED'


def _feature_flag_enabled() -> bool:
    return os.environ.get(_FEATURE_FLAG_NAME, '') == 'true_explicit_inventory_wiring_on'


def _affinity_points_enabled() -> bool:
    return os.environ.get(_AFFINITY_POINTS_FLAG, '') == 'true_explicit_affinity_points_on'


def _safety_envelope() -> dict[str, Any]:
    return {
        'shadow_only': True,
        'preview_only': True,
        'design_only': True,
        'runtime_attached': False,
        'db_write': False,
        'inventory_mutation_attempted': False,
        'inventory_mutation_committed': False,
        'affinity_points_mutation_attempted': False,
        'affinity_points_mutation_committed': False,
        'feature_flag_dependency': _FEATURE_FLAG_NAME,
        'feature_flag_currently_enabled': _feature_flag_enabled(),
        'affinity_points_flag_dependency': _AFFINITY_POINTS_FLAG,
        'affinity_points_flag_currently_enabled': _affinity_points_enabled(),
        'hidden_aliases_blocked': sorted(_FORBIDDEN_HERO_IDS),
    }


def shadow_inventory_apply(
    user_id: str,
    gift_id: str,
    hero_id: str,
    quantity: int,
    affinity_points_delta: int = 0,
    current_inventory_balance: int = 0,
    current_affinity_points: int = 0,
) -> dict[str, Any]:
    """Shadow / dry-run: returns a full plan of what would happen, no writes.

    Computes:
      - would_decrement_inventory (qty if pre-check OK; 0 otherwise)
      - would_increment_affinity (delta if allowed by policy; 0 otherwise)
      - would_write_affinity_state (False; always shadow)
      - rollback / compensation contract record
    """
    hid = (hero_id or '').strip().lower()
    uid = (user_id or '').strip()
    qty = max(0, int(quantity)) if isinstance(quantity, (int, float)) else 0
    pts = int(affinity_points_delta) if isinstance(affinity_points_delta, (int, float)) else 0
    inv = int(current_inventory_balance) if isinstance(current_inventory_balance, (int, float)) else 0
    cur_pts = int(current_affinity_points) if isinstance(current_affinity_points, (int, float)) else 0

    if hid in _FORBIDDEN_HERO_IDS:
        return {
            'task_origin': 'AF2-N-INVENTORY-WIRING-SHADOW',
            'preview_version': 'v1',
            'shadow_only': True,
            'user_id': uid, 'hero_id': hid, 'gift_id': (gift_id or '').strip(),
            'runtime_attached': False,
            'would_decrement_inventory': 0,
            'would_increment_affinity': 0,
            'would_write_affinity_state': False,
            'would_have_status': 'borea_filtered',
            'borea_filtered': True,
            'rollback_required': False,
            'compensation_required': False,
            'rollback_contract': {
                'reason': 'short_circuited_by_borea_filter',
                'steps_that_would_be_performed_in_future_live': [],
                'steps_to_reverse_in_rollback': [],
            },
            'safety_envelope': _safety_envelope(),
        }

    pre_check_pass = (qty == 0) or (inv >= qty)
    would_dec = qty if pre_check_pass else 0
    would_inc = pts if pre_check_pass else 0
    new_inv = inv - would_dec
    new_pts = cur_pts + would_inc

    return {
        'task_origin': 'AF2-N-INVENTORY-WIRING-SHADOW',
        'preview_version': 'v1',
        'shadow_only': True,
        'user_id': uid, 'hero_id': hid, 'gift_id': (gift_id or '').strip(),
        'quantity': qty, 'affinity_points_delta': pts,
        'current_inventory_balance': inv,
        'current_affinity_points': cur_pts,
        'pre_check_pass': pre_check_pass,
        'pre_check_reason': 'ok' if pre_check_pass else 'inventory_insufficient',
        'runtime_attached': False,
        'would_decrement_inventory': would_dec,
        'would_increment_affinity': would_inc,
        'would_write_affinity_state': False,
        'projected_inventory_after': new_inv,
        'projected_affinity_points_after': new_pts,
        'would_have_status': 'applied_shadow_only' if pre_check_pass else 'rejected_shadow_only',
        'borea_filtered': False,
        'atomicity_contract': 'single-document transaction in future live wiring; pre-check inventory >= qty BEFORE any mutation',
        'caps_contract': 'affinity_points capped per affinity_phase2_economy_cap_policy_draft_v1',
        'rollback_required': False,
        'compensation_required': False,
        'rollback_contract': {
            'reason': 'shadow_only_no_state_mutated',
            'steps_that_would_be_performed_in_future_live': [
                'BEGIN single-doc tx',
                f'inventory[{gift_id}] -= {would_dec}',
                f'affinity_points[{hid}] += {would_inc}',
                'append ledger row {tx_id, idempotency_key, inventory_mutated=true, affinity_points_mutated=true}',
                'COMMIT',
            ],
            'steps_to_reverse_in_rollback': [
                'lookup ledger row by tx_id',
                f'inventory[{gift_id}] += {would_dec}',
                f'affinity_points[{hid}] -= {would_inc}',
                'mark ledger row reversed=true',
            ],
            'compensation_path_when_rollback_unavailable': [
                'emit ledger row with compensation_required=true',
                'block downstream battle/UI consumption until reconciled',
            ],
        },
        'safety_envelope': _safety_envelope(),
    }


__all__ = ['shadow_inventory_apply']
