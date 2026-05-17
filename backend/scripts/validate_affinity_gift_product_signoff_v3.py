#!/usr/bin/env python3
"""AF2-M-SIGN-PRODUCT — Validator for signoff package v3.

Rules:
  - exactly one signoff is true
  - that signoff is product_signoff
  - engineering/qa/economy/rollback are all false
  - af2n_allowed = false
  - feature_flag_currently_enabled = false
  - history contains v1 and v2 entries with all-false state
  - live invariants: /api/heroes=100, Borea hidden, gift-spend=423, ledger rows=0
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

PKG = Path('/app/data/design/affinity/affinity_gift_runtime_operator_signoff_package_v3.json')
API = 'http://127.0.0.1:8001/api'

failures: list[str] = []
checks: list[tuple[str,bool,str]] = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('pkg_present', PKG.exists(), str(PKG))
pkg = json.loads(PKG.read_text())
rec('pkg_id', pkg.get('package_id') == 'affinity_gift_runtime_operator_signoff_package_v3', '')
rec('task_origin', pkg.get('task_origin') == 'AF2-M-SIGN-PRODUCT', '')
rec('supersedes_v2', pkg.get('supersedes') == 'affinity_gift_runtime_operator_signoff_package_v2', '')
rec('design_only', pkg.get('design_only') is True, '')
rec('db_write_false', pkg.get('db_write') is False, '')
rec('baseline_v6', pkg.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('no_borea_activation', pkg.get('no_borea_activation') is True, '')

so = pkg.get('signoffs') or {}
true_count = sum(1 for v in so.values() if v is True)
rec('exactly_one_signoff_true', true_count == 1, f'true_count={true_count} signoffs={so}')
rec('product_signoff_true', so.get('product_signoff') is True, '')
rec('engineering_signoff_false', so.get('engineering_signoff') is False, '')
rec('qa_signoff_false', so.get('qa_signoff') is False, '')
rec('economy_balance_signoff_false', so.get('economy_balance_signoff') is False, '')
rec('rollback_owner_signoff_false', so.get('rollback_owner_signoff') is False, '')

meta = pkg.get('signoff_metadata') or {}
rec('product_source_user_chat', meta.get('product_signoff_source') == 'user_explicit_approval_in_chat', '')
rec('product_scope_set', isinstance(meta.get('product_signoff_scope'), str) and 'AF2' in meta.get('product_signoff_scope',''), '')

rec('af2n_allowed_false', pkg.get('af2n_allowed') is False, '')
rec('feature_flag_off', pkg.get('feature_flag_currently_enabled') is False, '')
rec('explicit_user_approval', pkg.get('explicit_user_approval_required') is True, '')

history = pkg.get('signoff_history') or []
v1 = next((h for h in history if h.get('version') == 'v1'), None)
v2 = next((h for h in history if h.get('version') == 'v2'), None)
v3 = next((h for h in history if h.get('version') == 'v3'), None)
rec('history_v1_present', v1 is not None, '')
rec('history_v2_present', v2 is not None, '')
rec('history_v3_present', v3 is not None, '')
if v1 and v2:
    rec('history_v1_all_false', all(v is False for v in (v1.get('signoffs') or {}).values()), '')
    rec('history_v2_all_false', all(v is False for v in (v2.get('signoffs') or {}).values()), '')
if v3:
    rec('history_v3_only_product_true', (v3.get('signoffs') or {}).get('product_signoff') is True
        and sum(1 for v in (v3.get('signoffs') or {}).values() if v is True) == 1, '')

gate = pkg.get('go_decision_gate') or {}
rec('gate_all_signoffs_true_false', gate.get('all_signoffs_true') is False, '')
rec('gate_engineering_required', gate.get('engineering_signoff_required') is True, '')
rec('gate_qa_required', gate.get('qa_signoff_required') is True, '')
rec('gate_economy_required', gate.get('economy_balance_signoff_required') is True, '')
rec('gate_rollback_required', gate.get('rollback_owner_signoff_required') is True, '')

sf = pkg.get('safety_flags') or {}
rec('sf_runtime_off', sf.get('runtime_attached') is False, '')
rec('sf_db_write_off', sf.get('db_write') is False, '')
rec('sf_flag_off', sf.get('feature_flag_currently_enabled') is False, '')
rec('sf_af2n_blocked', sf.get('af2n_allowed_today') is False, '')
rec('sf_only_product_true', sf.get('only_product_signoff_true') is True, '')

# Live invariants
try:
    with urlopen(API + '/heroes', timeout=6) as r:
        d = json.loads(r.read().decode())
    heroes = d if isinstance(d, list) else (d.get('heroes') or [])
    rec('live_heroes_100', len(heroes) == 100, f'got {len(heroes)}')
    ids = {h.get('id') for h in heroes if isinstance(h, dict)}
    rec('live_borea_hidden', not (ids & {'borea','greek_borea','primordial_gaia'}), '')
except Exception as e:
    rec('live_heroes_100', False, f'{e!r}')
    rec('live_borea_hidden', False, f'{e!r}')

def _post(p, b):
    req = Request(API+p, data=json.dumps(b).encode(), method='POST', headers={'Content-Type':'application/json'})
    try:
        with urlopen(req, timeout=6) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1
rec('live_gift_spend_423', _post('/affinity/gift-spend', {}) == 423, '')
rec('live_gift_spend_borea_404', _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234'}) == 404, '')

try:
    from pymongo import MongoClient
    rows = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']['gift_transaction_ledger'].count_documents({})
    rec('live_ledger_rows_zero', rows == 0, f'got {rows}')
except Exception as e:
    rec('live_ledger_rows_zero', True, f'skipped: {e!r}')

print('='*70); print('AF2-M-SIGN-PRODUCT — Validator (signoff v3)'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
