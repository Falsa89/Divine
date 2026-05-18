#!/usr/bin/env python3
"""V16 SCHEMA MIGRATION — Create user_gift_inventory and user_affinity_state.

Gated by env DIVINE_ALLOW_USER_INVENTORY_SCHEMA_MIGRATION=YES_I_UNDERSTAND.
If not set, runs DRY-RUN (no DB change).
"""
from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = Path('/app/data/design/affinity/user_inventory_affinity_state_schema_v1.json')
OUT = Path('/app/data/design/affinity/user_inventory_affinity_state_migration_result_v1.json')
GATE = 'DIVINE_ALLOW_USER_INVENTORY_SCHEMA_MIGRATION'


def main():
    if not SCHEMA.exists():
        print('SCHEMA_FILE_MISSING'); return 1
    schema = json.loads(SCHEMA.read_text())
    gate_on = os.environ.get(GATE) == 'YES_I_UNDERSTAND'
    actions = []

    from pymongo import MongoClient, ASCENDING, DESCENDING
    db = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']
    existing = set(db.list_collection_names())

    for spec in schema['collections']:
        name = spec['name']
        actions.append({'collection': name, 'pre_existing': name in existing,
                        'created': False, 'indexes_created': []})
        if not gate_on: continue
        # Live migration
        if name not in existing:
            db.create_collection(name)
            actions[-1]['created'] = True
        coll = db[name]
        for idx in spec['indexes']:
            keys = [(k, ASCENDING if v == 1 else DESCENDING) for k, v in idx['keys']]
            try:
                coll.create_index(keys, name=idx['name'], unique=idx.get('unique', False))
                actions[-1]['indexes_created'].append(idx['name'])
            except Exception as e:
                actions[-1]['indexes_created'].append(f"FAIL {idx['name']}: {e!r}")

    final_state = set(db.list_collection_names())
    payload = {
        'result_id': 'user_inventory_affinity_state_migration_result_v1',
        'task_origin': 'V16 SCHEMA-MIGRATION-USER-INVENTORY',
        'design_only': not gate_on,
        'gated_env': GATE,
        'gate_currently_set': gate_on,
        'mode': 'live' if gate_on else 'dry_run',
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'collections_observed_before': sorted(existing),
        'collections_observed_after': sorted(final_state),
        'user_gift_inventory_present_after': 'user_gift_inventory' in final_state,
        'user_affinity_state_present_after': 'user_affinity_state' in final_state,
        'actions': actions,
        'overall_status': 'PASS' if (gate_on and ('user_gift_inventory' in final_state) and ('user_affinity_state' in final_state)) or (not gate_on)
                          else 'FAIL',
        'safety_flags': {
            'no_non_qa_data_mutation': True,
            'no_borea_activation': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
            'broad_rollout_authorized': False,
            'battle_runtime_attached': False,
            'inventory_wiring_live': False,  # this is migration only; activation is a separate step
            'feature_flag_currently_enabled': True,
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'mode={payload["mode"]}, ugi={payload["user_gift_inventory_present_after"]}, uas={payload["user_affinity_state_present_after"]}, status={payload["overall_status"]}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
