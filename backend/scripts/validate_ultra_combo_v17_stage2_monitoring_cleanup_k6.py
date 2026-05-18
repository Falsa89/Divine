#!/usr/bin/env python3
"""ULTRA-COMBO V17 — Composite validator."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

SCRIPTS = Path('/app/backend/scripts')
API = 'http://127.0.0.1:8001/api'

SUBTASKS = [
    ('V17-PREFLIGHT',                          'validate_af2n_v17_preflight.py'),
    ('AF2-N-INVENTORY-EXTENDED-MONITORING-V17','validate_af2n_inventory_extended_monitoring_v17.py'),
    ('AF2-N-STAGE2-APPLY',                     'validate_af2n_stage2_5_10pct_apply_result.py'),
    ('AF2-N-STAGE2-MONITORING-V17',            'validate_af2n_stage2_monitoring_v17.py'),
    ('SUITE-SUPERSEDENCE-CLEANUP',             'validate_validator_suite_supersedence_cleanup.py'),
    ('AF2-L-K6-LOCUST-READINESS-V17',          'validate_af2n_v17_k6_locust_readiness.py'),
    ('V17-ROLLBACK-READINESS',                 'validate_af2n_v17_rollback_readiness.py'),
    ('SAFETY-ROLLUP-L',                        'validate_collection_affinity_runtime_activation_rollup_v12.py'),
]

failures = []; checks = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

def run_one(s):
    p = SCRIPTS / s
    if not p.exists(): return 127
    try:
        r = subprocess.run(['python3', str(p)], capture_output=True, text=True, timeout=240)
        return r.returncode
    except Exception: return -1

for tag, script in SUBTASKS:
    rec(f'subtask:{tag}', run_one(script) == 0, '')

def _get(p):
    try:
        with urlopen(API + p, timeout=6) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None

def _post(p, b):
    payload = json.dumps(b).encode(); headers = {'Content-Type': 'application/json'}
    req = Request(API + p, data=payload, method='POST', headers=headers)
    try:
        with urlopen(req, timeout=6) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1

code, data = _get('/heroes')
rec('live_heroes_reachable', code in (200, 304), f'got {code}')
if isinstance(data, list):
    rec('live_heroes_count_100', len(data) == 100, f'got {len(data)}')
    ids = {h.get('id') for h in data if isinstance(h, dict)}
    rec('live_borea_hidden', not (ids & {'borea','greek_borea','primordial_gaia'}), '')

code, status = _get('/affinity/gift-spend/canary-status')
rec('live_canary_status_200', code == 200, f'got {code}')
if isinstance(status, dict):
    rec('flag_on', status.get('feature_flag_currently_enabled') is True, '')
    rec('inv_enabled', status.get('inventory_mutation_enabled') is True, '')
    rec('pts_enabled', status.get('affinity_points_mutation_enabled') is True, '')
    rec('combat_off', status.get('applied_to_combat') is False, '')
    rec('battle_off', status.get('battle_runtime_attached') is False, '')
    rec('buffs_off', status.get('buffs_enabled') is False, '')
    rec('allowlist_size_le_200', status.get('canary_allowlist_size', 0) <= 200, '')
    rec('ledger_cap_le_1000', status.get('canary_ledger_cap', 0) <= 1000, '')
    rec('ledger_within_cap', status.get('ledger_total_rows', 0) <= status.get('canary_ledger_cap', 0), '')

rec('live_gift_spend_borea_404',
    _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'v17composit01','user_id':'user_canary_001'}) == 404, '')
rec('live_gift_spend_non_allowlist_423',
    _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'v17composit02','user_id':'unauth_v17_x'}) == 423, '')

try:
    from pymongo import MongoClient
    db = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']
    coll = db['gift_transaction_ledger']
    total = coll.count_documents({}); canary = coll.count_documents({'canary': True})
    rec('db_only_canary_writes', total == canary, f'total={total} canary={canary}')
    rec('db_within_cap', total <= 1000, f'total={total}')
    inv_mut = coll.count_documents({'inventory_mutated': True})
    aff_mut = coll.count_documents({'affinity_points_mutated': True})
    rec('db_inv_aff_equal', inv_mut == aff_mut, f'inv={inv_mut} aff={aff_mut}')
    rec('db_no_buffs', coll.count_documents({'buffs_activated': True}) == 0, '')
    rec('db_no_battle', coll.count_documents({'battle_wiring_attached': True}) == 0, '')
    rec('db_no_borea_hero', coll.count_documents({'hero_id': {'$in': ['borea','greek_borea','primordial_gaia']}}) == 0, '')
    cols = set(db.list_collection_names())
    rec('ugi_present', 'user_gift_inventory' in cols, '')
    rec('uas_present', 'user_affinity_state' in cols, '')
    rec('ugi_no_negative', db['user_gift_inventory'].count_documents({'quantity': {'$lt': 0}}) == 0, '')
except Exception as e:
    rec('db_only_canary_writes', False, f'{e!r}')

try:
    out = subprocess.run(
        ['git','-C','/app','diff','--stat','--',
         'backend/battle_engine.py','backend/battle_core.py',
         'frontend/app/combat.tsx','backend/game_systems.py',
         'backend/synergy_system.py'],
        capture_output=True, text=True, timeout=10)
    rec('battle_files_unchanged', out.stdout.strip() == '', f'diff={out.stdout!r}')
except Exception as e:
    rec('battle_files_unchanged', False, f'{e!r}')

for path in ('/app/backend/battle_engine.py', '/app/backend/battle_core.py',
             '/app/frontend/app/combat.tsx'):
    p = Path(path)
    if p.exists():
        body = p.read_text()
        rec(f'no_shadow_adapter_in:{p.name}',
            'affinity_gift_inventory_shadow_adapter' not in body, '')
        rec(f'no_gift_spend_route_in:{p.name}',
            'register_affinity_gift_spend_skeleton_routes' not in body, '')

print('='*70); print('ULTRA-COMBO V17 — Stage2 monitoring/cleanup/k6 composite'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print(f'Overall: {"PASS" if not failures else "FAIL"}')

OUT = Path('/app/backend/reports/ultra_combo_v17_validator_summary_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({
    'combo_id': 'ULTRA_COMBO_V17',
    'task_origin': 'V17-INVENTORY-EXTENDED-MONITORING+STAGE2-EXPANSION+SUITE-CLEANUP+K6-READINESS+SAFETY-ROLLUP-L',
    'design_only': False, 'runtime_attached': True,
    'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
    'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
    'checks_total': len(checks),
    'checks_passed': sum(1 for _, o, _ in checks if o),
    'checks_failed': len(failures),
    'failures': failures,
    'overall': 'PASS' if not failures else 'FAIL',
    'safety_flags': {
        'runtime_attached': True, 'broad_rollout_authorized': False,
        'inventory_wiring_live': True, 'inventory_mutation_enabled': True,
        'affinity_points_mutation_enabled': True,
        'battle_runtime_attached': False, 'applied_to_combat': False,
        'buffs_enabled': False, 'feature_flag_currently_enabled': True,
        'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
    }
}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
sys.exit(0 if not failures else 1)
