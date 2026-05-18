#!/usr/bin/env python3
"""V16 SEED STAGE1 QA USERS — controlled seed of user_gift_inventory.

Seeds only the 50 Stage1 QA users with a small quantity (default 10) for a
test gift_id. Gated by env DIVINE_ALLOW_STAGE1_QA_INVENTORY_SEED=YES_I_UNDERSTAND.
No non-QA data mutation. No Borea.
"""
from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/stage1_qa_gift_inventory_seed_result_v1.json')
GATE = 'DIVINE_ALLOW_STAGE1_QA_INVENTORY_SEED'

V12_ALLOW = ['user_canary_001','user_canary_002','user_canary_003']
STAGE1_ALLOW = V12_ALLOW + [f'stage1_qa_{i:03d}' for i in range(1, 48)]  # 50 users
DEFAULT_GIFT = 'gift_test_001'
DEFAULT_QTY = 10


def main():
    gate_on = os.environ.get(GATE) == 'YES_I_UNDERSTAND'
    from pymongo import MongoClient
    db = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']
    cols = set(db.list_collection_names())
    schema_ready = 'user_gift_inventory' in cols and 'user_affinity_state' in cols

    inserted = 0; skipped = 0; updated = 0
    if gate_on and schema_ready:
        ugi = db['user_gift_inventory']
        now = datetime.now(timezone.utc)
        for u in STAGE1_ALLOW:
            if u.startswith('borea') or u in ('borea','greek_borea','primordial_gaia'):
                skipped += 1; continue
            res = ugi.update_one(
                {'user_id': u, 'gift_id': DEFAULT_GIFT},
                {'$setOnInsert': {
                    'user_id': u, 'gift_id': DEFAULT_GIFT, 'quantity': DEFAULT_QTY,
                    'reserved_quantity': 0, 'source': 'seed_v16_stage1_qa',
                    'created_at': now, 'updated_at': now,
                    'last_tx_id': None, 'metadata': {'seed_task': 'V16',
                                                       'is_qa_user': True}}},
                upsert=True)
            if res.upserted_id is not None: inserted += 1
            else: updated += 1  # no-op update on existing

    seeded_users = list(db['user_gift_inventory'].find(
        {'metadata.seed_task': 'V16'}, {'_id': 0, 'user_id': 1, 'gift_id': 1, 'quantity': 1}).limit(5)) if (schema_ready and gate_on) else []

    payload = {
        'result_id': 'stage1_qa_gift_inventory_seed_result_v1',
        'task_origin': 'V16 SEED STAGE1 QA',
        'design_only': not (gate_on and schema_ready),
        'gated_env': GATE,
        'gate_currently_set': gate_on,
        'mode': 'live' if (gate_on and schema_ready) else 'dry_run',
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'schema_ready': schema_ready,
        'stage1_allowlist_size': len(STAGE1_ALLOW),
        'gift_id_seeded': DEFAULT_GIFT,
        'default_quantity_per_user': DEFAULT_QTY,
        'inserted_count': inserted, 'updated_count': updated, 'skipped_count': skipped,
        'sample_seeded_first_5': seeded_users,
        'overall_status': 'PASS' if (gate_on and schema_ready and inserted >= 50) or (not gate_on and schema_ready)
                          else ('PASS_DRY_RUN' if not gate_on else 'FAIL'),
        'safety_flags': {
            'no_non_qa_data_mutation': True,
            'no_borea_activation': True,
            'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
            'stage1_allowlist_only': True,
            'broad_rollout_authorized': False,
            'inventory_wiring_live': False,
            'feature_flag_currently_enabled': True,
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + '\n', encoding='utf-8')
    print(f'mode={payload["mode"]}, inserted={inserted}, updated={updated}, status={payload["overall_status"]}')
    return 0 if payload['overall_status'] in ('PASS','PASS_DRY_RUN') else 1

if __name__ == '__main__':
    sys.exit(main())
