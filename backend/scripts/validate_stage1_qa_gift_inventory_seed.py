#!/usr/bin/env python3
"""V16 SEED — Validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/stage1_qa_gift_inventory_seed_result_v1.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'stage1_qa_gift_inventory_seed_result_v1', '')
rec('task', r.get('task_origin') == 'V16 SEED STAGE1 QA', '')
rec('schema_ready', r.get('schema_ready') is True, '')
rec('gate_on', r.get('gate_currently_set') is True, '')
rec('mode_live', r.get('mode') == 'live', f"mode={r.get('mode')}")
rec('overall_pass', r.get('overall_status') == 'PASS', '')
rec('allowlist_50', r.get('stage1_allowlist_size') == 50, '')
rec('inserted_min_50_or_already_seeded',
    (r.get('inserted_count', 0) + r.get('updated_count', 0)) >= 50, '')
rec('qty_min_5', r.get('default_quantity_per_user', 0) >= 5, '')

from pymongo import MongoClient
db = MongoClient('mongodb://localhost:27017')['divine_waifus']
if 'user_gift_inventory' in db.list_collection_names():
    seeded = db['user_gift_inventory'].count_documents({'metadata.seed_task':'V16'})
    rec('seeded_count_50', seeded == 50, f'got={seeded}')
    bad_borea = db['user_gift_inventory'].count_documents({'gift_id':{'$in':['borea','greek_borea','primordial_gaia']}})
    rec('no_borea_gift_in_seed', bad_borea == 0, '')
    neg = db['user_gift_inventory'].count_documents({'quantity':{'$lt':0}})
    rec('no_negative_qty', neg == 0, '')

sf = r.get('safety_flags') or {}
for k in ('no_non_qa_data_mutation','no_borea_activation','stage1_allowlist_only','feature_flag_currently_enabled'):
    rec(f'sf_{k}', sf.get(k) is True, '')
for k in ('broad_rollout_authorized','inventory_wiring_live'):
    rec(f'sf_{k}_false', sf.get(k) is False, '')

print('='*70); print('V16 SEED — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
