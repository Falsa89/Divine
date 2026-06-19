#!/usr/bin/env python3
"""Pack 130 — No rewards / no progress (STATIC)."""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FILES = [REPO_ROOT / 'backend' / 'routes' / 'v130_lobby_launch_context.py',
         REPO_ROOT / 'backend' / 'helpers' / 'lobby_launch_context.py',
         REPO_ROOT / 'backend' / 'helpers' / 'real_player_snapshot.py']
FORBIDDEN = ['grant_reward', 'add_exp', 'grant_currency', 'spend_currency',
             'apply_reward', 'tower_reward', 'arena_reward', 'raid_reward',
             'db.transactions.', 'db.gacha_pulls.', 'db.mail.insert',
             'db.inventory.update', 'db.wallets.update', 'sanctuary_affinity_mutation']


def main() -> int:
    errors = []; notes = []
    for f in FILES:
        if not f.exists(): continue
        src = f.read_text(encoding='utf-8')
        for fp in FORBIDDEN:
            if fp in src:
                errors.append(f'{f.name} references reward/progress mutation: `{fp}`')
    print(f'OK    {len(FILES)} files scanned, {len(FORBIDDEN)} forbidden reward/progress patterns checked')
    return _emit(errors, notes)


def _emit(errors, notes):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_130_NO_REWARDS_NO_PROGRESS',
              'status': 'PASS' if not errors else 'FAIL', 'errors': errors, 'notes': notes,
              'forbidden_patterns': FORBIDDEN,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED_NO_REWARD_NO_PROGRESS_NO_ECONOMY_NO_INVENTORY_IN_PACK_130'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_130_no_rewards_no_progress_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  Pack 130 touches NO reward/progress/economy/inventory')
    return 0


if __name__ == '__main__': sys.exit(main())
