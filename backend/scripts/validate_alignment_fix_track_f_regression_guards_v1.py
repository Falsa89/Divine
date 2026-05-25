#!/usr/bin/env python3
# ALIGNMENT_FIX Track F — regression no-reopen guards.
import json, sys, hashlib
from pathlib import Path
P = Path('/app/data/design/audit/alignment_fix/regression_no_reopen_guards_v1.json')
SCRIPTS = Path('/app/backend/scripts')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_F_REGRESSION_GUARD_AND_NO_REOPEN_RULES_READY'
    guards = d['no_reopen_guards']
    assert len(guards) >= 9
    must_ids = {'GUARD-SAFE-PREVIEWS-NAV','GUARD-GACHA-HIDE-ARTIFACT-CONSTELLATION',
                'GUARD-GACHA-LOCK-PREMIUM-TARGETED','GUARD-ARTIFACTS-REDIRECT',
                'GUARD-SHOP-LOCKED','GUARD-ITEM-SHOP-LOCKED','GUARD-BATTLEPASS-LOCKED',
                'GUARD-VIP-LOCKED','GUARD-MENU-DEV-HIDDEN','GUARD-SOUL-FORGE-4PLUS-RULES'}
    have_ids = {g['id'] for g in guards}
    missing = must_ids - have_ids
    assert not missing, f'missing guards: {missing}'
    # ogni validator citato deve esistere
    referenced = set()
    for g in guards:
        v = g.get('validator')
        if v: referenced.add(v)
    for v in referenced:
        assert (SCRIPTS / v).exists(), f'referenced validator not found: {v}'
    assert d['db_writes'] == 0 and d['backend_changes'] == 0
    print(f"[PASS] ALIGN-FIX Track F regression guards \u2014 guards={len(guards)} validators={len(referenced)}")
    return 0
if __name__ == '__main__': sys.exit(main())
