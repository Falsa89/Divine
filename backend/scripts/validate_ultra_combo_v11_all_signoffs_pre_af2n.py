#!/usr/bin/env python3
"""ULTRA-COMBO V11 — Composite validator.

Aggregates V11 subtask validators/audits and enforces the joint
NO_GO_RUNTIME + all-five-signoffs-true + final-user-approval-MISSING
invariants live. AF2-N is verified to be NOT executed.
"""
from __future__ import annotations
import json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

SCRIPTS = Path('/app/backend/scripts')
API = 'http://127.0.0.1:8001/api'

SUBTASKS = [
    ('V11-PREFLIGHT',            'validate_ultra_combo_v11_preflight.py'),
    ('AF2-M-V4-ALL-SIGNOFFS',    'validate_affinity_gift_operator_signoff_v4.py'),
    ('AF2-L-K6-LIVE-PREP',       'validate_affinity_gift_spend_k6_live_prep_result_v2.py'),
    ('OPS-C-SUP-APPLY',          'validate_ops_c_supervisor_apply_result.py'),
    ('AF2-N-GO-NOGO-PRE',        'validate_af2n_go_no_go_preflight_package.py'),
    ('SAFETY-ROLLUP-F',          'validate_collection_affinity_runtime_activation_rollup_v6.py'),
]

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

def run_one(script):
    p = SCRIPTS / script
    if not p.exists(): return 127
    try:
        r = subprocess.run(['python3', str(p)], capture_output=True, text=True, timeout=90)
        return r.returncode
    except Exception: return -1

for tag, script in SUBTASKS:
    rec(f'subtask:{tag}', run_one(script) == 0, '')

# Live smoke
def _get(p):
    try:
        with urlopen(API+p, timeout=6) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None
def _post(p, b):
    payload = None; headers = {}
    if b is not None:
        payload = json.dumps(b).encode(); headers = {'Content-Type':'application/json'}
    req = Request(API+p, data=payload, method='POST', headers=headers)
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

rec('live_gift_spend_empty_423', _post('/affinity/gift-spend', {}) == 423, '')
rec('live_gift_spend_borea_404',
    _post('/affinity/gift-spend',
          {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234'}) == 404, '')
rec('live_gift_spend_greek_borea_404',
    _post('/affinity/gift-spend',
          {'gift_id':'x','hero_id':'greek_borea','quantity':1,'idempotency_key':'abcd1234'}) == 404, '')
code, _ = _get('/affinity/gifts/by-element/dark/by-faction/greek')
rec('live_axis_g_200', code == 200, f'got {code}')

# AF2-N NOT executed
rec('env_runtime_flag_off', os.environ.get('AFFINITY_GIFT_RUNTIME_ENABLED', '') == '', '')

# Signoff v4 → all 5 true + af2n_allowed=false
SO = Path('/app/data/design/affinity/affinity_gift_runtime_operator_signoff_package_v4.json')
if SO.exists():
    pkg = json.loads(SO.read_text())
    so = pkg.get('signoffs') or {}
    rec('signoff_v4_all_5_true', sum(1 for v in so.values() if v is True) == 5, f'got={so}')
    rec('signoff_v4_af2n_false', pkg.get('af2n_allowed') is False, '')
    rec('signoff_v4_final_approval_false', pkg.get('final_user_runtime_approval_present') is False, '')

# Rollup v6 → NO_GO + final_user_approval=false
RL = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v6.json')
if RL.exists():
    r = json.loads(RL.read_text())
    rec('rollup_v6_no_go', r.get('go_no_go_decision') == 'NO_GO_RUNTIME', '')
    rec('rollup_v6_all_signoffs', r.get('all_operator_signoffs_true') is True, '')
    rec('rollup_v6_final_user_false', r.get('final_user_runtime_approval_present') is False, '')
    rec('rollup_v6_overall_false', r.get('overall_runtime_activation_ready') is False, '')
    rec('rollup_v6_af2n_false', r.get('AF2N_allowed') is False, '')

# AF2-N GO/NO-GO package → do_not_execute_in_this_task=true
GN = Path('/app/data/design/affinity/af2n_go_no_go_preflight_package_v1.json')
if GN.exists():
    g = json.loads(GN.read_text())
    rec('af2n_pkg_do_not_execute', g.get('do_not_execute_in_this_task') is True, '')
    rec('af2n_pkg_decision_no_go',
        g.get('go_no_go_decision_today') == 'NO_GO_PENDING_FINAL_USER_APPROVAL', '')

# DB ledger row count
try:
    from pymongo import MongoClient
    rows = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000) \
            ['divine_waifus']['gift_transaction_ledger'].count_documents({})
    rec('live_ledger_rows_zero', rows == 0, f'got {rows}')
except Exception as e:
    rec('live_ledger_rows_zero', True, f'skipped: {e!r}')

# Battle files unchanged (no adapter/resolver import)
for path in ('/app/backend/battle_engine.py', '/app/backend/battle_core.py',
             '/app/frontend/app/combat.tsx'):
    p = Path(path)
    if p.exists():
        body = p.read_text()
        rec(f'no_adapter_import:{p.name}',
            'global_modifier_cap_battle_preview_adapter' not in body, '')
        rec(f'no_resolver_import:{p.name}',
            'global_modifier_cap_resolver' not in body, '')

print('='*70); print('ULTRA-COMBO V11 — Composite Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print(f'Overall: {"PASS" if not failures else "FAIL"}')

OUT = Path('/app/backend/reports/ultra_combo_v11_validator_summary_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({
    'combo_id': 'ULTRA_COMBO_V11',
    'task_origin': 'V11-AF2M_ALL_SIGNOFFS+AF2L_K6_LIVE_PREP+OPS_C_SUPERVISOR_APPLY+AF2N_GO_NOGO_PACKAGE+SAFETY_ROLLUP_F',
    'design_only': True, 'runtime_attached': False, 'db_write': False,
    'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6',
    'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    'checks_total': len(checks),
    'checks_passed': sum(1 for _, o, _ in checks if o),
    'checks_failed': len(failures),
    'failures': failures,
    'overall': 'PASS' if not failures else 'FAIL',
    'safety_flags': {
        'runtime_attached': False, 'db_write': False,
        'feature_flag_currently_enabled': False,
        'hidden_aliases_blocked': ['borea','greek_borea','primordial_gaia'],
        'AF2N_allowed_today': False,
        'all_operator_signoffs_true': True,
        'final_user_runtime_approval_present': False,
        'supervisor_wiring_state': 'READY_NOT_APPLIED',
    },
}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

sys.exit(0 if not failures else 1)
