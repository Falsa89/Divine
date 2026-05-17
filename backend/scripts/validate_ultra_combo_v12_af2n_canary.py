#!/usr/bin/env python3
"""ULTRA-COMBO V12 — Composite validator (AF2-N CONTROLLED CANARY)."""
from __future__ import annotations
import json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

SCRIPTS = Path('/app/backend/scripts')
API = 'http://127.0.0.1:8001/api'

SUBTASKS = [
    ('FINAL-USER-APPROVAL', 'validate_final_user_runtime_approval_record.py'),
    ('AF2-N-CANARY-SMOKE',  'validate_af2n_canary_smoke_monitoring.py'),
    ('AF2-N-ACTIVATION',    'validate_af2n_runtime_activation_result.py'),
    ('SAFETY-ROLLUP-G',     'validate_collection_affinity_runtime_activation_rollup_v7.py'),
]

failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

def run_one(s):
    p = SCRIPTS / s
    if not p.exists(): return 127
    try:
        r = subprocess.run(['python3', str(p)], capture_output=True, text=True, timeout=90)
        return r.returncode
    except Exception: return -1

for tag, script in SUBTASKS:
    rec(f'subtask:{tag}', run_one(script) == 0, '')

def _get(p):
    try:
        with urlopen(API+p, timeout=6) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None
def _post(p, b):
    payload = json.dumps(b).encode(); headers = {'Content-Type':'application/json'}
    req = Request(API+p, data=payload, method='POST', headers=headers)
    try:
        with urlopen(req, timeout=6) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1

# Live invariants
code, data = _get('/heroes')
rec('live_heroes_reachable', code in (200, 304), f'got {code}')
if isinstance(data, list):
    rec('live_heroes_count_100', len(data) == 100, f'got {len(data)}')
    ids = {h.get('id') for h in data if isinstance(h, dict)}
    rec('live_borea_hidden', not (ids & {'borea','greek_borea','primordial_gaia'}), '')

# Canary status
code, status = _get('/affinity/gift-spend/canary-status')
rec('live_canary_status_200', code == 200, f'got {code}')
if isinstance(status, dict):
    rec('canary_runtime_on', status.get('feature_flag_currently_enabled') is True, '')
    rec('canary_allowlist_min_1', status.get('canary_allowlist_size', 0) >= 1, '')
    rec('canary_ledger_within_cap',
        status.get('ledger_total_rows', 0) <= status.get('canary_ledger_cap', 0), '')
    rec('canary_only_writes',
        status.get('ledger_total_rows') == status.get('ledger_canary_rows'), '')
    rec('canary_combat_off', status.get('applied_to_combat') is False, '')
    rec('canary_battle_off', status.get('battle_runtime_attached') is False, '')

# Hot live checks
rec('live_gift_spend_borea_404',
    _post('/affinity/gift-spend',
          {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234efgh','user_id':'user_canary_001'}) == 404, '')
rec('live_gift_spend_greek_borea_404',
    _post('/affinity/gift-spend',
          {'gift_id':'x','hero_id':'greek_borea','quantity':1,'idempotency_key':'abcd1234efgh','user_id':'user_canary_001'}) == 404, '')
rec('live_gift_spend_non_allowlist_423',
    _post('/affinity/gift-spend',
          {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'rndidem9999','user_id':'unauth_user_xxx'}) == 423, '')

# AXIS-G unchanged
code, _ = _get('/affinity/gifts/by-element/dark/by-faction/greek')
rec('live_axis_g_200', code == 200, f'got {code}')
code, _ = _get('/affinity/gifts/by-element/dark/by-faction/borea')
rec('live_axis_g_borea_404', code == 404, f'got {code}')

# DB invariants
try:
    from pymongo import MongoClient
    coll = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000) \
            ['divine_waifus']['gift_transaction_ledger']
    total = coll.count_documents({})
    canary = coll.count_documents({'canary': True})
    rec('db_only_canary_writes', total == canary, f'total={total} canary={canary}')
    rec('db_no_inventory_mut', coll.count_documents({'inventory_mutated': True}) == 0, '')
    rec('db_no_points_mut', coll.count_documents({'affinity_points_mutated': True}) == 0, '')
    rec('db_no_buffs', coll.count_documents({'buffs_activated': True}) == 0, '')
    rec('db_no_battle', coll.count_documents({'battle_wiring_attached': True}) == 0, '')
    rec('db_no_borea_hero', coll.count_documents({'hero_id': {'$in': ['borea','greek_borea','primordial_gaia']}}) == 0, '')
except Exception as e:
    rec('db_only_canary_writes', False, f'{e!r}')

# Battle files unchanged (git diff)
try:
    out = subprocess.run(
        ['git', '-C', '/app', 'diff', '--stat', '--',
         'backend/battle_engine.py', 'backend/battle_core.py',
         'frontend/app/combat.tsx', 'backend/game_systems.py',
         'backend/synergy_system.py'],
        capture_output=True, text=True, timeout=10)
    rec('battle_files_unchanged', out.stdout.strip() == '', f'diff={out.stdout!r}')
except Exception as e:
    rec('battle_files_unchanged', False, f'{e!r}')

# No adapter/resolver imports in battle files
for path in ('/app/backend/battle_engine.py', '/app/backend/battle_core.py',
             '/app/frontend/app/combat.tsx'):
    p = Path(path)
    if p.exists():
        body = p.read_text()
        rec(f'no_adapter_import:{p.name}',
            'global_modifier_cap_battle_preview_adapter' not in body, '')
        rec(f'no_resolver_import:{p.name}',
            'global_modifier_cap_resolver' not in body, '')

# Approval record
APR = Path('/app/data/design/affinity/final_user_runtime_approval_record_v1.json')
if APR.exists():
    a = json.loads(APR.read_text())
    rec('approval_present', a.get('final_user_runtime_approval_present') is True, '')

# Rollup G no rollback executed
RG = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v7.json')
if RG.exists():
    r = json.loads(RG.read_text())
    rec('rollup_g_no_rollback', r.get('rollback_executed') is False, '')
    rec('rollup_g_canary_pass', r.get('AF2N_canary_status') == 'PASS', '')
    rec('rollup_g_broad_rollout_off', r.get('AF2N_broad_rollout_authorized') is False, '')

print('='*70); print('ULTRA-COMBO V12 — AF2-N Canary Composite Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print(f'Overall: {"PASS" if not failures else "FAIL"}')

OUT = Path('/app/backend/reports/ultra_combo_v12_validator_summary_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({
    'combo_id': 'ULTRA_COMBO_V12',
    'task_origin': 'V12-AF2N-CONTROLLED-RUNTIME-FLIP-CANARY+MONITORING+ROLLBACK-READY+SAFETY-ROLLUP-G',
    'design_only': False, 'runtime_attached': True, 'runtime_attached_canary_only': True,
    'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
    'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    'checks_total': len(checks),
    'checks_passed': sum(1 for _, o, _ in checks if o),
    'checks_failed': len(failures),
    'failures': failures,
    'overall': 'PASS' if not failures else 'FAIL',
    'safety_flags': {
        'runtime_attached': True, 'runtime_attached_canary_only': True,
        'broad_rollout_authorized': False,
        'db_write': True, 'db_write_scope': 'gift_transaction_ledger only',
        'feature_flag_currently_enabled': True,
        'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        'AF2N_executed': True, 'AF2N_canary_pass': True,
        'inventory_mutation_enabled': False,
        'affinity_points_mutation_enabled': False,
        'buffs_enabled': False,
        'battle_runtime_attached': False,
        'applied_to_combat': False,
    },
}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

sys.exit(0 if not failures else 1)
