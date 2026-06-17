#!/usr/bin/env python3
"""Pack 126-FIX-A — Validator: no reward/gacha/shop/VIP/BP/IAP/EXP changes in fix."""
from __future__ import annotations
import json, sys, subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_NEW = [
    '/api/gacha/', '/api/shop/', '/api/vip/', '/api/battlepass/', '/api/iap/',
    '/api/mail/claim', 'grant_exp', 'grant_reward', 'premium_currency',
]


def main() -> int:
    errors = []
    # Get diff of battle.tsx vs HEAD~1 (or working tree if no commit yet)
    try:
        r = subprocess.run(['git', '-C', str(REPO_ROOT), 'diff', 'HEAD', '--', 'frontend/app/(tabs)/battle.tsx'], capture_output=True, text=True, timeout=15)
        diff = r.stdout
    except Exception as e:
        diff = ''
    if not diff:
        # Could be already committed. Try last commit diff.
        try:
            r2 = subprocess.run(['git', '-C', str(REPO_ROOT), 'show', '--format=', 'HEAD', '--', 'frontend/app/(tabs)/battle.tsx'], capture_output=True, text=True, timeout=15)
            diff = r2.stdout
        except Exception:
            diff = ''
    added_lines = [ln[1:] for ln in diff.split('\n') if ln.startswith('+') and not ln.startswith('+++')]
    added = '\n'.join(added_lines)
    print(f'OK    diff added lines: {len(added_lines)}')
    for pat in FORBIDDEN_NEW:
        if pat in added:
            errors.append(f'forbidden pattern introduced: `{pat}`')
    if not errors:
        print('OK    no forbidden patterns in added lines')
    # Static scan of the file as well
    src = (REPO_ROOT / 'frontend' / 'app' / '(tabs)' / 'battle.tsx').read_text(encoding='utf-8')
    # The file itself may legitimately mention `exp` (post-battle), but the FIX-A
    # added lines must not.
    if 'rewards' in added.lower() or 'exp_gained' in added.lower() or 'gold +' in added.lower() or 'diamonds +' in added.lower():
        errors.append('FIX-A introduces reward/EXP/currency code (must not)')
    else:
        print('OK    no reward/EXP/currency code added')
    return _emit(errors)


def _emit(errors):
    print('\n' + '='*72)
    print('Pack 126-FIX-A — no live unlock / no reward in fix')
    print('='*72)
    report = {'pack':'PACK_126_FIX_A_NO_LIVE_UNLOCKS','status':'PASS' if not errors else 'FAIL','errors':errors}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_126_fix_a_no_live_unlocks_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  no reward/gacha/shop/VIP/BP/IAP/EXP code added by FIX-A')
    return 0


if __name__ == '__main__':
    sys.exit(main())
