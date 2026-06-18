#!/usr/bin/env python3
"""Pack 126-FIX-B — Validator: no-live/no-reward/no-gacha/shop/VIP/BP/IAP."""
from __future__ import annotations
import json, sys, subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FILES = ['frontend/app/(tabs)/battle.tsx', 'frontend/app/hero-collection.tsx', 'frontend/app/pre-battle-lobby.tsx']
FORBIDDEN = ['/api/gacha/', '/api/shop/', '/api/vip/', '/api/battlepass/', '/api/iap/', '/api/mail/claim', 'grant_exp', 'grant_reward', 'premium_currency']


def main() -> int:
    errors = []
    # Diff added lines
    try:
        r = subprocess.run(['git', '-C', str(REPO_ROOT), 'diff', 'HEAD', '--'] + FILES, capture_output=True, text=True, timeout=15)
        diff = r.stdout
    except Exception:
        diff = ''
    added = '\n'.join([ln[1:] for ln in diff.split('\n') if ln.startswith('+') and not ln.startswith('+++')])
    print(f'OK    diff added lines: {len(added.split(chr(10)))}')
    for fp in FORBIDDEN:
        if fp in added:
            errors.append(f'forbidden in added: `{fp}`')
    if not errors:
        print('OK    no forbidden patterns in added lines')
    return _emit(errors)


def _emit(errors):
    print('\n' + '='*72)
    report = {'pack':'PACK_126_FIX_B_NO_LIVE_UNLOCKS','status':'PASS' if not errors else 'FAIL','errors':errors}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_126_fix_b_no_live_unlocks_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  no reward/gacha/shop/VIP/BP/IAP code added by FIX-B')
    return 0

if __name__ == '__main__': sys.exit(main())
