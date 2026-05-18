#!/usr/bin/env python3
"""ULTRA-COMBO V20 — Composite validator."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

SCRIPTS = Path('/app/backend/scripts')
API = 'http://127.0.0.1:8001/api'

SUBTASKS = [
    ('V20-PREFLIGHT',                              'validate_af2n_v20_preflight.py'),
    ('AF2-N-STAGE4-INTERNAL-BETA-PLAN',            'validate_af2n_stage4_internal_beta_plan.py'),
    ('AF2-N-V20-ROLLBACK-DRILLS',                  'validate_af2n_v20_rollback_drill_result.py'),
    ('AF2-N-STAGE4-SIGNOFF-PACKAGE-V5',            'validate_af2n_stage4_signoff_package_v5.py'),
    ('AF2-L-LOCUST-EXTENDED-LOW-IMPACT-V20',       'validate_af2n_v20_locust_extended_result.py'),
    ('AF2-N-PUBLIC-UI-PREVIEW-QA-A11Y-V20',        'audit_affinity_gifts_public_preview_qa_a11y.py'),
    ('SAFETY-ROLLUP-O',                            'validate_collection_affinity_runtime_activation_rollup_v15.py'),
]

failures = []; checks = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

def run_one(s):
    p = SCRIPTS / s
    if not p.exists(): return 127
    try:
        r = subprocess.run(['python3', str(p)], capture_output=True, text=True, timeout=300)
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
    rec('combat_off', status.get('applied_to_combat') is False, '')
    rec('battle_off', status.get('battle_runtime_attached') is False, '')
    rec('buffs_off', status.get('buffs_enabled') is False, '')
    rec('allowlist_le_500', status.get('canary_allowlist_size', 0) <= 500, '')
    rec('cap_le_5000', status.get('canary_ledger_cap', 0) <= 5000, '')
    # Crucially: Stage4 NOT applied means size should still be 200 (Stage3)
    rec('stage4_NOT_applied_size_eq_200', status.get('canary_allowlist_size', 0) == 200, '')
    rec('stage4_NOT_applied_cap_eq_2500', status.get('canary_ledger_cap', 0) == 2500, '')
    rec('ledger_within_cap', status.get('ledger_total_rows', 0) <= status.get('canary_ledger_cap', 0), '')

rec('live_borea_404', _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'v20cmp0001','user_id':'stage3_qa_001'}) == 404, '')
rec('live_non_allow_423', _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'v20cmp0002','user_id':'unauth_v20cmp'}) == 423, '')

try:
    from pymongo import MongoClient
    db = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']
    coll = db['gift_transaction_ledger']
    total = coll.count_documents({}); canary = coll.count_documents({'canary': True})
    rec('db_only_canary', total == canary, f'total={total} canary={canary}')
    rec('db_within_hard_cap', total <= 5000, f'total={total}')
    rec('db_inv_aff_equal', coll.count_documents({'inventory_mutated': True}) == coll.count_documents({'affinity_points_mutated': True}), '')
    rec('db_no_buffs', coll.count_documents({'buffs_activated': True}) == 0, '')
    rec('db_no_battle', coll.count_documents({'battle_wiring_attached': True}) == 0, '')
    rec('db_no_borea_hero', coll.count_documents({'hero_id': {'$in': ['borea','greek_borea','primordial_gaia']}}) == 0, '')
    rec('ugi_no_negative', db['user_gift_inventory'].count_documents({'quantity': {'$lt': 0}}) == 0, '')
    # Stage4 seed must NOT exist (not applied)
    rec('no_stage4_seed_docs', db['user_gift_inventory'].count_documents({'metadata.seed_task': 'V20_STAGE4'}) == 0, '')
except Exception as e:
    rec('db_only_canary', False, f'{e!r}')

try:
    out = subprocess.run(['git','-C','/app','diff','--stat','--',
        'backend/battle_engine.py','backend/battle_core.py',
        'frontend/app/combat.tsx','backend/game_systems.py','backend/synergy_system.py'],
        capture_output=True, text=True, timeout=10)
    rec('battle_files_unchanged', out.stdout.strip() == '', f'diff={out.stdout!r}')
except Exception as e:
    rec('battle_files_unchanged', False, f'{e!r}')

# Verify Stage4 plan + signoff = PLAN-ONLY
plan = Path('/app/data/design/affinity/af2n_stage4_internal_beta_plan_v1.json')
so = Path('/app/data/design/affinity/af2n_stage4_signoff_package_v5.json')
if plan.exists():
    d = json.loads(plan.read_text())
    rec('plan_plan_only_true', d.get('plan_only') is True, '')
    rec('plan_stage4_applied_false', d.get('stage4_applied') is False, '')
if so.exists():
    d = json.loads(so.read_text())
    rec('signoff_stage4_apply_allowed_false', d.get('stage4_apply_allowed') is False, '')
    rec('signoff_final_user_approval_false', d.get('final_user_stage4_apply_approval') is False, '')

# Verify no apply/rollback script for Stage4 was created (PLAN-ONLY contract)
rec('no_stage4_apply_script', not Path('/app/backend/scripts/apply_af2n_stage4_internal_beta.py').exists())
rec('no_stage4_rollback_script', not Path('/app/backend/scripts/rollback_af2n_stage4_internal_beta.py').exists())

print('='*70); print('ULTRA-COMBO V20 — Stage4 PLAN-ONLY + Drills + Signoffs + Locust ext + UI A11y'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- "+note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print(f'Overall: {"PASS" if not failures else "FAIL"}')

OUT = Path('/app/backend/reports/ultra_combo_v20_validator_summary_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({
    'combo_id': 'ULTRA_COMBO_V20',
    'task_origin': 'V20-STAGE4-PLAN-ONLY+DRILLS+SIGNOFFS-V5+LOCUST-EXT+UI-A11Y+SAFETY-ROLLUP-O',
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
        'stage4_applied': False, 'stage4_apply_allowed': False,
        'public_spend_ui': False, 'public_ui_preview_readonly_qa_a11y_audited': True,
        'inventory_wiring_live': True, 'inventory_mutation_enabled': True,
        'affinity_points_mutation_enabled': True,
        'battle_runtime_attached': False, 'applied_to_combat': False,
        'buffs_enabled': False, 'feature_flag_currently_enabled': True,
        'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
    }
}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
sys.exit(0 if not failures else 1)
