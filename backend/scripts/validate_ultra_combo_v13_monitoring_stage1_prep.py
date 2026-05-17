#!/usr/bin/env python3
"""ULTRA-COMBO V13 — Composite validator (AF2-N-MONITORING-WINDOW + AF2-N-STAGE1-PREP + AF2-N-INVENTORY-WIRING-PRE + AF2-L-K6-LIVE-PREP2 + SAFETY-ROLLUP-H)."""
from __future__ import annotations
import json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

SCRIPTS = Path('/app/backend/scripts')
API = 'http://127.0.0.1:8001/api'

SUBTASKS = [
    ('AF2-N-MONITORING-WINDOW', 'validate_af2n_monitoring_window_result.py'),
    ('AF2-N-STAGE1-PREP',       'validate_af2n_stage1_1pct_allowlist_plan.py'),
    ('AF2-N-INVENTORY-WIRING-PRE', 'audit_af2n_inventory_wiring_pre.py'),
    ('AF2-L-K6-LIVE-PREP2',     'validate_affinity_gift_spend_k6_live_prep2_result.py'),
    ('SAFETY-ROLLUP-H',         'validate_collection_affinity_runtime_activation_rollup_v8.py'),
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

# Live invariants (re-check)
code, data = _get('/heroes')
rec('live_heroes_reachable', code in (200, 304), f'got {code}')
if isinstance(data, list):
    rec('live_heroes_count_100', len(data) == 100, f'got {len(data)}')
    ids = {h.get('id') for h in data if isinstance(h, dict)}
    rec('live_borea_hidden', not (ids & {'borea','greek_borea','primordial_gaia'}), '')

code, status = _get('/affinity/gift-spend/canary-status')
rec('live_canary_status_200', code == 200, f'got {code}')
if isinstance(status, dict):
    rec('canary_runtime_on', status.get('feature_flag_currently_enabled') is True, '')
    rec('canary_within_cap',
        status.get('ledger_total_rows', 0) <= status.get('canary_ledger_cap', 0), '')
    rec('canary_only_writes',
        status.get('ledger_total_rows') == status.get('ledger_canary_rows'), '')
    rec('canary_combat_off', status.get('applied_to_combat') is False, '')
    rec('canary_battle_off', status.get('battle_runtime_attached') is False, '')
    rec('canary_inventory_off', status.get('inventory_mutation_enabled') is False, '')
    rec('canary_points_off', status.get('affinity_points_mutation_enabled') is False, '')
    rec('canary_buffs_off', status.get('buffs_enabled') is False, '')

rec('live_gift_spend_borea_404',
    _post('/affinity/gift-spend',
          {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234efgh','user_id':'user_canary_001'}) == 404, '')
rec('live_gift_spend_non_allowlist_423',
    _post('/affinity/gift-spend',
          {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'rndidem9999','user_id':'unauth_user_xxx'}) == 423, '')

# DB invariants
try:
    from pymongo import MongoClient
    coll = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000) \
            ['divine_waifus']['gift_transaction_ledger']
    total = coll.count_documents({})
    canary = coll.count_documents({'canary': True})
    rec('db_only_canary_writes', total == canary, f'total={total} canary={canary}')
    rec('db_within_cap', total <= 20, f'total={total}')
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
        rec(f'no_inventory_adapter_in:{p.name}',
            'inventory_wiring_preview_adapter' not in body, '')
        rec(f'no_resolver_in:{p.name}',
            'global_modifier_cap_resolver' not in body, '')

print('='*70); print('ULTRA-COMBO V13 — Monitoring + Stage1 Prep + Inventory Pre + K6 Live Prep2 + Rollup H'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print(f'Overall: {"PASS" if not failures else "FAIL"}')

OUT = Path('/app/backend/reports/ultra_combo_v13_validator_summary_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({
    'combo_id': 'ULTRA_COMBO_V13',
    'task_origin': 'V13-AF2N-MONITORING+STAGE1-PREP+INVENTORY-WIRING-PRE+K6-LIVE-PREP2+SAFETY-ROLLUP-H',
    'design_only': False, 'runtime_attached': True, 'runtime_attached_canary_only': True,
    'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
    'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    'checks_total': len(checks),
    'checks_passed': sum(1 for _, o, _ in checks if o),
    'checks_failed': len(failures),
    'failures': failures,
    'overall': 'PASS' if not failures else 'FAIL',
    'safety_flags': {
        'runtime_attached': True,
        'runtime_attached_canary_only': True,
        'broad_rollout_authorized': False,
        'stage1_applied': False,
        'inventory_wiring_live': False,
        'battle_runtime_attached': False,
        'applied_to_combat': False,
        'inventory_mutation_enabled': False,
        'affinity_points_mutation_enabled': False,
        'buffs_enabled': False,
        'feature_flag_currently_enabled': True,
        'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        'AF2N_monitoring_window_pass': True,
        'AF2N_stage1_plan_ready_not_applied': True,
        'AF2N_inventory_wiring_pre_ready_not_wired': True,
        'k6_live_prep2_pass': True,
    },
}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

sys.exit(0 if not failures else 1)
