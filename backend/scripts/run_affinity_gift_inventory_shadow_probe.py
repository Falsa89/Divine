#!/usr/bin/env python3
"""AF2-N-INVENTORY-WIRING-SHADOW — Dry-run probe.

Loads the shadow adapter dynamically (NEVER live-imports it from any
production route) and exercises many input combinations to produce a
report: pre-check pass/fail, Borea filter, rollback contract present, etc.

Guarantees NO DB writes: counts ledger rows before/after to assert.
"""
from __future__ import annotations
import importlib.util, json, sys, time
from datetime import datetime, timezone
from pathlib import Path

ADAPTER = Path('/app/backend/data/affinity_gift_inventory_shadow_adapter.py')
OUT = Path('/app/data/design/affinity/affinity_gift_inventory_shadow_wiring_result_v1.json')


def main():
    spec = importlib.util.spec_from_file_location('shadow_inv', ADAPTER)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

    pre_total = post_total = -1
    try:
        from pymongo import MongoClient
        coll = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']['gift_transaction_ledger']
        pre_total = coll.count_documents({})
    except Exception:
        coll = None

    scenarios = [
        {'name':'normal_ok',           'args':('user_canary_001','gift_x','greek_zeus',1,5,100,50)},
        {'name':'normal_zero_qty',     'args':('user_canary_001','gift_x','greek_zeus',0,0,100,50)},
        {'name':'insufficient_inv',    'args':('user_canary_001','gift_x','greek_zeus',5,5,2,50)},
        {'name':'huge_qty',            'args':('user_canary_001','gift_x','greek_zeus',9999,500,1000,50)},
        {'name':'negative_qty',        'args':('user_canary_001','gift_x','greek_zeus',-3,0,100,50)},
        {'name':'borea',               'args':('user_canary_001','gift_x','borea',1,5,100,50)},
        {'name':'greek_borea',         'args':('user_canary_001','gift_x','greek_borea',1,5,100,50)},
        {'name':'primordial_gaia',     'args':('user_canary_001','gift_x','primordial_gaia',1,5,100,50)},
        {'name':'stage1_qa_user',      'args':('stage1_qa_007','gift_x','greek_zeus',2,3,10,20)},
    ]
    outputs = []
    started = time.monotonic()
    for s in scenarios:
        try:
            out = mod.shadow_inventory_apply(*s['args'])
        except Exception as e:
            out = {'error': repr(e)}
        outputs.append({'name': s['name'], 'args': list(s['args']), 'output': out})

    if coll is not None:
        try: post_total = coll.count_documents({})
        except Exception: pass

    invariants = {
        'ledger_unchanged': pre_total == post_total and pre_total >= 0,
        'all_runtime_attached_false': all(o['output'].get('runtime_attached') is False for o in outputs if 'output' in o and isinstance(o['output'], dict)),
        'all_shadow_only_true': all(o['output'].get('shadow_only') is True for o in outputs if 'output' in o and isinstance(o['output'], dict)),
        'all_db_write_false': all(((o['output'].get('safety_envelope') or {}).get('db_write')) is False for o in outputs if isinstance(o.get('output'), dict)),
        'borea_filtered_correctly': all((o['output'].get('borea_filtered') is True
                                          and o['output'].get('would_decrement_inventory') == 0
                                          and o['output'].get('would_increment_affinity') == 0)
                                         for o in outputs if o['name'] in ('borea','greek_borea','primordial_gaia')),
        'rollback_contract_present_all': all(isinstance(o['output'].get('rollback_contract'), dict)
                                              for o in outputs if isinstance(o.get('output'), dict)),
        'insufficient_inv_rejected': next(o['output'].get('would_have_status') == 'rejected_shadow_only'
                                          for o in outputs if o['name'] == 'insufficient_inv'),
        'normal_ok_applied_shadow': next(o['output'].get('would_have_status') == 'applied_shadow_only'
                                          for o in outputs if o['name'] == 'normal_ok'),
    }

    payload = {
        'result_id': 'affinity_gift_inventory_shadow_wiring_result_v1',
        'task_origin': 'AF2-N-INVENTORY-WIRING-SHADOW',
        'design_only': True, 'runtime_attached': False, 'db_write': False,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'elapsed_seconds': round(time.monotonic() - started, 4),
        'ledger_row_count_before': pre_total,
        'ledger_row_count_after': post_total,
        'scenarios': outputs,
        'invariants': invariants,
        'overall_status': 'PASS' if all(invariants.values()) else 'FAIL',
        'safety_flags': {
            'runtime_attached': False, 'db_write': False,
            'inventory_mutation_enabled': False,
            'affinity_points_mutation_enabled': False,
            'buffs_enabled': False,
            'battle_runtime_attached': False,
            'applied_to_combat': False,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Inventory shadow probe: scenarios={len(scenarios)}, status={payload["overall_status"]}, ledger_unchanged={invariants["ledger_unchanged"]}')
    print(f'Result: {OUT}')
    return 0 if payload['overall_status'] == 'PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
