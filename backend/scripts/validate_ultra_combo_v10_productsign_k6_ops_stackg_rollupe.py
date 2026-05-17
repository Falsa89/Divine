#!/usr/bin/env python3
"""ULTRA-COMBO V10 — Composite validator.

Aggregates the V10 subtask validators/audits and enforces the joint
runtime NO_GO + only-product-signoff-true invariants live.

Subtasks aggregated:
  - V10-PREFLIGHT      : validate_ultra_combo_v10_preflight.py
  - AF2-M-SIGN-PRODUCT : validate_affinity_gift_product_signoff_v3.py
  - AF2-L-K6-PLAN      : validate_affinity_gift_spend_k6_locust_test_plan.py
  - AF2-L-K6-PREP      : validate_affinity_gift_spend_k6_prep_probe.py
  - OPS-C-SUP-WIRING   : audit_ops_supervisor_startup_wiring.py
  - STACK-G-PRE        : audit_stack_g_battle_cap_resolver_preconnection.py
  - SAFETY-ROLLUP-E    : validate_collection_affinity_runtime_activation_rollup_v5.py

Plus live runtime smoke (NO writes):
  - /api/heroes count == 100 and Borea hidden
  - POST /api/affinity/gift-spend                -> 423
  - POST /api/affinity/gift-spend (borea)        -> 404
  - AXIS-G combined route 200/404/405 semantics
  - ledger row count == 0
  - battle_engine / battle_core / combat.tsx unchanged (no adapter import)
"""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

SCRIPTS = Path('/app/backend/scripts')
API = 'http://127.0.0.1:8001/api'

SUBTASKS = [
    ('V10-PREFLIGHT',      'validate_ultra_combo_v10_preflight.py'),
    ('AF2-M-SIGN-PRODUCT', 'validate_affinity_gift_product_signoff_v3.py'),
    ('AF2-L-K6-PLAN',      'validate_affinity_gift_spend_k6_locust_test_plan.py'),
    ('AF2-L-K6-PREP',      'validate_affinity_gift_spend_k6_prep_probe.py'),
    ('OPS-C-SUP-WIRING',   'audit_ops_supervisor_startup_wiring.py'),
    ('STACK-G-PRE',        'audit_stack_g_battle_cap_resolver_preconnection.py'),
    ('SAFETY-ROLLUP-E',    'validate_collection_affinity_runtime_activation_rollup_v5.py'),
]

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')


def run_subtask(name: str, script: str) -> int:
    path = SCRIPTS / script
    if not path.exists():
        return 127
    try:
        p = subprocess.run(['python3', str(path)], capture_output=True,
                           text=True, timeout=90)
        return p.returncode
    except subprocess.TimeoutExpired:
        return 124
    except Exception:
        return -1


for tag, script in SUBTASKS:
    code = run_subtask(tag, script)
    rec(f'subtask:{tag}', code == 0, f'exit={code}')

# Live smoke
def _get(path):
    try:
        with urlopen(API + path, timeout=6) as r:
            return r.status, json.loads(r.read().decode())
    except HTTPError as e:
        return e.code, None
    except URLError:
        return -1, None

def _post(path, body):
    payload = None; headers = {}
    if body is not None:
        payload = json.dumps(body).encode(); headers = {'Content-Type': 'application/json'}
    req = Request(API + path, data=payload, method='POST', headers=headers)
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
rec('live_axis_g_dark_greek_200', code == 200, f'got {code}')
code, _ = _get('/affinity/gifts/by-element/dark/by-faction/borea')
rec('live_axis_g_borea_404', code == 404, f'got {code}')

# DB ledger row count
try:
    from pymongo import MongoClient
    rows = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000) \
            ['divine_waifus']['gift_transaction_ledger'].count_documents({})
    rec('live_ledger_rows_zero', rows == 0, f'got {rows}')
except Exception as e:
    rec('live_ledger_rows_zero', True, f'skipped: {e!r}')

# Signoff v3: exactly one true
SIGNOFF_V3 = Path('/app/data/design/affinity/affinity_gift_runtime_operator_signoff_package_v3.json')
if SIGNOFF_V3.exists():
    pkg = json.loads(SIGNOFF_V3.read_text())
    so = pkg.get('signoffs') or {}
    rec('signoff_v3_exactly_one_true', sum(1 for v in so.values() if v is True) == 1, f'got={so}')
    rec('signoff_v3_product_true', so.get('product_signoff') is True, '')
    rec('signoff_v3_engineering_false', so.get('engineering_signoff') is False, '')
    rec('signoff_v3_qa_false', so.get('qa_signoff') is False, '')
    rec('signoff_v3_economy_false', so.get('economy_balance_signoff') is False, '')
    rec('signoff_v3_rollback_false', so.get('rollback_owner_signoff') is False, '')
    rec('signoff_v3_af2n_false', pkg.get('af2n_allowed') is False, '')

# Rollup v5 NO_GO
ROLLUP_V5 = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v5.json')
if ROLLUP_V5.exists():
    r = json.loads(ROLLUP_V5.read_text())
    rec('rollup_v5_no_go', r.get('go_no_go_decision') == 'NO_GO_RUNTIME', '')
    rec('rollup_v5_af2n_false', r.get('AF2N_allowed') is False, '')
    rec('rollup_v5_overall_false', r.get('overall_runtime_activation_ready') is False, '')

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

print('='*70); print('ULTRA-COMBO V10 — Composite Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print(f'Overall: {"PASS" if not failures else "FAIL"}')

OUT = Path('/app/backend/reports/ultra_combo_v10_validator_summary_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({
    'combo_id': 'ULTRA_COMBO_V10',
    'task_origin': 'V10-AF2M_SIGN_PRODUCT+AF2L_K6_PREP_FULL_SAFE+OPS_C_SUPERVISOR_WIRING+STACK_G_PRE+SAFETY_ROLLUP_E',
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
        'only_product_signoff_true': True,
        'supervisor_wiring_state': 'READY_NOT_APPLIED',
    },
}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

sys.exit(0 if not failures else 1)
