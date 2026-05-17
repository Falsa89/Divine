#!/usr/bin/env python3
"""AF2-M-SIGN-PRODUCT — Idempotent apply script.

Reads the existing signoff_package_v3.json, asserts only product_signoff
is true, and "signs" by injecting the signed_at_utc timestamp. Idempotent.

No DB write. No runtime mutation. No AF2-N. No feature flag flip.
"""
from __future__ import annotations
import json, sys
from datetime import datetime, timezone
from pathlib import Path

PKG = Path('/app/data/design/affinity/affinity_gift_runtime_operator_signoff_package_v3.json')

if not PKG.exists():
    print(f'FATAL: signoff package v3 missing at {PKG}')
    sys.exit(2)

pkg = json.loads(PKG.read_text())
so = pkg.get('signoffs') or {}

# Strict gate: only product must be true; all others must be false.
expected = {
    'product_signoff': True,
    'engineering_signoff': False,
    'qa_signoff': False,
    'economy_balance_signoff': False,
    'rollback_owner_signoff': False,
}
for k, v in expected.items():
    if so.get(k) is not v:
        print(f'FATAL: signoffs.{k} expected {v}, got {so.get(k)!r}')
        sys.exit(3)

if pkg.get('af2n_allowed') is not False:
    print('FATAL: af2n_allowed must be false')
    sys.exit(4)
if pkg.get('feature_flag_currently_enabled') is not False:
    print('FATAL: feature_flag_currently_enabled must be false')
    sys.exit(5)

meta = pkg.setdefault('signoff_metadata', {})
if not meta.get('signed_at_utc'):
    meta['signed_at_utc'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

PKG.write_text(json.dumps(pkg, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('AF2-M-SIGN-PRODUCT applied (idempotent).')
print(f'  product_signoff = {so.get("product_signoff")}')
print(f'  engineering_signoff = {so.get("engineering_signoff")}')
print(f'  qa_signoff = {so.get("qa_signoff")}')
print(f'  economy_balance_signoff = {so.get("economy_balance_signoff")}')
print(f'  rollback_owner_signoff = {so.get("rollback_owner_signoff")}')
print(f'  af2n_allowed = {pkg.get("af2n_allowed")}')
print(f'  signed_at_utc = {meta.get("signed_at_utc")}')
sys.exit(0)
