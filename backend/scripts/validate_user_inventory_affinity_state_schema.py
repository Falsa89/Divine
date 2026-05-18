#!/usr/bin/env python3
"""V16 SCHEMA MIGRATION — Validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/user_inventory_affinity_state_migration_result_v1.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'user_inventory_affinity_state_migration_result_v1', '')
rec('task', r.get('task_origin') == 'V16 SCHEMA-MIGRATION-USER-INVENTORY', '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('overall_pass', r.get('overall_status') == 'PASS', '')
rec('ugi_present', r.get('user_gift_inventory_present_after') is True, '')
rec('uas_present', r.get('user_affinity_state_present_after') is True, '')
rec('mode_live', r.get('mode') == 'live', f"mode={r.get('mode')}")
rec('gate_set', r.get('gate_currently_set') is True, '')

from pymongo import MongoClient
db = MongoClient('mongodb://localhost:27017')['divine_waifus']
for coll, idx_names in [
    ('user_gift_inventory', ['idx_user_gift_unique','idx_user_id','idx_gift_id','idx_updated_at']),
    ('user_affinity_state', ['idx_user_hero_unique','idx_user_id_aff','idx_hero_id_aff','idx_affinity_tier']),
]:
    cols = set(db.list_collection_names())
    rec(f'{coll}_present_db', coll in cols, '')
    if coll in cols:
        idx_info = {i['name']: i for i in db[coll].list_indexes()}
        for n in idx_names:
            rec(f'{coll}:{n}', n in idx_info, '')

sf = r.get('safety_flags') or {}
for k in ('no_non_qa_data_mutation','no_borea_activation','feature_flag_currently_enabled'):
    rec(f'sf_{k}', sf.get(k) is True, '')
for k in ('broad_rollout_authorized','battle_runtime_attached','inventory_wiring_live'):
    rec(f'sf_{k}_false', sf.get(k) is False, '')

print('='*70); print('V16 SCHEMA MIGRATION — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
