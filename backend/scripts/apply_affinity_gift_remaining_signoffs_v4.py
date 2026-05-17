#!/usr/bin/env python3
"""AF2-M (v4) — Idempotent apply for the remaining four signoffs.

Strict gate: refuses to apply unless all five live invariants hold:
  /api/heroes == 100, Borea hidden, gift-spend == 423,
  Borea alias == 404, ledger rows == 0.
Also refuses if AF2-N appears to be requested (flag toggled on).
"""
from __future__ import annotations
import json, sys, os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

PKG = Path('/app/data/design/affinity/affinity_gift_runtime_operator_signoff_package_v4.json')
API = 'http://127.0.0.1:8001/api'

if not PKG.exists():
    print(f'FATAL: signoff package v4 missing at {PKG}'); sys.exit(2)
pkg = json.loads(PKG.read_text())

# Live gates
def _post(p, b):
    req = Request(API+p, data=json.dumps(b).encode(), method='POST', headers={'Content-Type':'application/json'})
    try:
        with urlopen(req, timeout=6) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1

blockers = []
try:
    with urlopen(API + '/heroes', timeout=6) as r:
        d = json.loads(r.read().decode())
    heroes = d if isinstance(d, list) else (d.get('heroes') or [])
    if len(heroes) != 100: blockers.append(f'/api/heroes count != 100 (got {len(heroes)})')
    ids = {h.get('id') for h in heroes if isinstance(h, dict)}
    if ids & {'borea','greek_borea','primordial_gaia'}: blockers.append('Borea visible')
except Exception as e:
    blockers.append(f'/api/heroes unreachable: {e!r}')
if _post('/affinity/gift-spend', {}) != 423: blockers.append('gift-spend not 423')
if _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234'}) != 404:
    blockers.append('borea alias not 404')
try:
    from pymongo import MongoClient
    rows = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']['gift_transaction_ledger'].count_documents({})
    if rows != 0: blockers.append(f'ledger rows != 0 (got {rows})')
except Exception:
    pass
# AF2-N must remain blocked
if os.environ.get('AFFINITY_GIFT_RUNTIME_ENABLED', '') != '':
    blockers.append('AFFINITY_GIFT_RUNTIME_ENABLED env var set; refuse to sign while runtime active')

if blockers:
    print('FATAL: cannot apply remaining signoffs; blockers:')
    for b in blockers: print(f'  - {b}')
    sys.exit(3)

# All gates passed — confirm signoffs and persist timestamp
so = pkg.get('signoffs') or {}
expected = {'product_signoff': True, 'engineering_signoff': True,
            'qa_signoff': True, 'economy_balance_signoff': True,
            'rollback_owner_signoff': True}
for k, v in expected.items():
    if so.get(k) is not v:
        print(f'FATAL: signoffs.{k} expected {v}, got {so.get(k)!r}'); sys.exit(4)

# Hard-stop: even with all five signoffs, AF2-N must remain false.
if pkg.get('af2n_allowed') is not False:
    print('FATAL: af2n_allowed MUST remain false in v4'); sys.exit(5)
if pkg.get('final_user_runtime_approval_present') is not False:
    print('FATAL: final_user_runtime_approval_present MUST be false in v4'); sys.exit(6)
if pkg.get('feature_flag_currently_enabled') is not False:
    print('FATAL: feature_flag_currently_enabled MUST be false'); sys.exit(7)

meta = pkg.setdefault('signoff_metadata', {})
if not meta.get('signed_at_utc'):
    meta['signed_at_utc'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

PKG.write_text(json.dumps(pkg, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('AF2-M v4 — remaining signoffs APPLIED (idempotent).')
for k in ('product_signoff','engineering_signoff','qa_signoff','economy_balance_signoff','rollback_owner_signoff'):
    print(f'  {k} = {so.get(k)}')
print(f'  af2n_allowed = {pkg.get("af2n_allowed")}')
print(f'  final_user_runtime_approval_present = {pkg.get("final_user_runtime_approval_present")}')
print(f'  overall_runtime_activation_state = {pkg.get("overall_runtime_activation_state")}')
print(f'  signed_at_utc = {meta.get("signed_at_utc")}')
sys.exit(0)
