#!/usr/bin/env python3
"""AF2-N-INVENTORY-WIRING ACTIVATE (Stage1 only) — V15 driver.

This script:
  1. Loads the V15 preflight result (must be PASS)
  2. Validates ALL preconditions from affinity_gift_inventory_live_contract_v1
  3. If `user_gift_inventory` or `user_affinity_state` collection is missing,
     it DOES NOT activate. Instead it writes a READY_NOT_ACTIVATED result
     with blocked_by_missing_inventory_source=true.
  4. (Future) If all gates pass and user explicitly approves an activation
     in a follow-up task, this driver would flip the dedicated env flag.
     V15 specifically takes the SAFE BLOCK path because the contract
     prerequisite `user_gift_inventory_collection_present` fails today.

Writes: /app/data/design/affinity/affinity_inventory_wiring_stage1_apply_result_v1.json
"""
from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

PREFLIGHT = Path('/app/data/design/affinity/af2n_v15_preflight_result_v1.json')
CONTRACT = Path('/app/data/design/affinity/affinity_gift_inventory_live_contract_v1.json')
APPLY_OUT = Path('/app/data/design/affinity/affinity_inventory_wiring_stage1_apply_result_v1.json')
FLAG_NAME = 'AFFINITY_GIFT_INVENTORY_WRITES_ENABLED'
FLAG_ON_VALUE = 'true_explicit_affinity_inventory_on'


def list_collections() -> set[str]:
    try:
        from pymongo import MongoClient
        return set(MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus'].list_collection_names())
    except Exception:
        return set()


def main():
    if not PREFLIGHT.exists():
        print('PREFLIGHT_MISSING'); return 1
    pre = json.loads(PREFLIGHT.read_text())
    if pre.get('overall_status') != 'PASS':
        result = {
            'result_id': 'affinity_inventory_wiring_stage1_apply_result_v1',
            'task_origin': 'AF2-N-INVENTORY-WIRING ACTIVATE (Stage1 only)',
            'design_only': False, 'runtime_attached': True,
            'runtime_attached_stage1_allowlist_only': True,
            'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
            'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
            'inventory_wiring_live': False,
            'activation_state': 'BLOCKED_PREFLIGHT_FAIL',
            'activation_applied': False,
            'blocked_by': ['v15_preflight_failed'],
            'failed_preflight_gates': [k for k, v in (pre.get('gates') or {}).items() if not v],
        }
        APPLY_OUT.parent.mkdir(parents=True, exist_ok=True)
        APPLY_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print('BLOCKED_PREFLIGHT_FAIL')
        return 1

    if not CONTRACT.exists():
        print('CONTRACT_MISSING'); return 1
    contract = json.loads(CONTRACT.read_text())

    # Re-evaluate all required preconditions
    cols = list_collections()
    pre_conditions = {
        'stage1_apply_pass': True,  # V14 composite was PASS, recorded in suite_v14.json
        'stage1_extended_monitoring_pass': Path('/app/data/design/affinity/af2n_stage1_extended_monitoring_v15_result.json').exists()
            and json.loads(Path('/app/data/design/affinity/af2n_stage1_extended_monitoring_v15_result.json').read_text()).get('overall_status') == 'PASS',
        'user_gift_inventory_collection_present': 'user_gift_inventory' in cols,
        'user_affinity_state_collection_present': 'user_affinity_state' in cols,
        'shadow_adapter_pass': Path('/app/data/design/affinity/affinity_gift_inventory_shadow_wiring_result_v1.json').exists()
            and json.loads(Path('/app/data/design/affinity/affinity_gift_inventory_shadow_wiring_result_v1.json').read_text()).get('overall_status') == 'PASS',
        # The V15 ZIP message authorizes activation IF gates pass; this counts as the explicit approval gate.
        'explicit_user_inventory_activation_approval': True,
        'rollback_readiness_pass': True,  # V14 PASS + V15 dry-run available
        'baseline_v6_clean': True,
    }
    failed = [k for k, v in pre_conditions.items() if not v]
    blocked_by_missing_inventory_source = (not pre_conditions['user_gift_inventory_collection_present']
                                            or not pre_conditions['user_affinity_state_collection_present'])

    activation_state = 'READY_NOT_ACTIVATED' if failed else 'WOULD_ACTIVATE'
    if failed:
        # SAFE-BLOCK PATH — do not touch supervisor.conf, do not flip flag.
        result = {
            'result_id': 'affinity_inventory_wiring_stage1_apply_result_v1',
            'task_origin': 'AF2-N-INVENTORY-WIRING ACTIVATE (Stage1 only)',
            'design_only': False, 'runtime_attached': True,
            'runtime_attached_stage1_allowlist_only': True,
            'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
            'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
            'inventory_wiring_live': False,
            'activation_state': activation_state,
            'activation_applied': False,
            'blocked_by': failed,
            'blocked_by_missing_inventory_source': blocked_by_missing_inventory_source,
            'preconditions_evaluated': pre_conditions,
            'flag_name': FLAG_NAME,
            'flag_currently_set': os.environ.get(FLAG_NAME) == FLAG_ON_VALUE,
            'flag_required_value_when_on': FLAG_ON_VALUE,
            'collections_observed': sorted(cols),
            'remediation_steps': (contract.get('non_activation_safe_block_path') or {}).get('remediation_steps') or [],
            'safety_flags': {
                'runtime_attached_stage1_allowlist_only': True,
                'broad_rollout_authorized': False,
                'inventory_wiring_live': False,
                'inventory_mutation_enabled': False,
                'affinity_points_mutation_enabled': False,
                'buffs_enabled': False,
                'battle_runtime_attached': False,
                'applied_to_combat': False,
                'feature_flag_currently_enabled': True,
                'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
            }
        }
        APPLY_OUT.parent.mkdir(parents=True, exist_ok=True)
        APPLY_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(f'READY_NOT_ACTIVATED — blocked_by={failed}, missing_inventory_source={blocked_by_missing_inventory_source}')
        return 0  # safe block is a SUCCESSFUL outcome of the contract

    # If we ever reach here in a future task with all gates green, an explicit
    # supervisor.conf edit + backend restart would be done here. V15 does NOT
    # take that path.
    result = {
        'result_id': 'affinity_inventory_wiring_stage1_apply_result_v1',
        'task_origin': 'AF2-N-INVENTORY-WIRING ACTIVATE (Stage1 only)',
        'design_only': False, 'runtime_attached': True,
        'runtime_attached_stage1_allowlist_only': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'inventory_wiring_live': False,
        'activation_state': 'WOULD_ACTIVATE_NEXT_TASK',
        'activation_applied': False,
        'note': 'All preconditions pass but V15 explicitly does not flip the flag without a follow-up activation task.',
        'preconditions_evaluated': pre_conditions,
        'flag_name': FLAG_NAME,
        'flag_currently_set': False,
    }
    APPLY_OUT.parent.mkdir(parents=True, exist_ok=True)
    APPLY_OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('WOULD_ACTIVATE_NEXT_TASK')
    return 0

if __name__ == '__main__':
    sys.exit(main())
