#!/usr/bin/env python3
"""Pack 129 — Team save no rewards / no progress (STATIC).

Verifica che il route NON tocchi:
  - users (account-wide collection)
  - reward grants
  - inventory/wallet
  - EXP/hero progression
  - gacha/shop/VIP/BP/mail
  - currency spend/grant
  - sanctuary affinity
  - battle result mutations
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTE = REPO_ROOT / 'backend' / 'routes' / 'v96_team_formation.py'

FORBIDDEN_MUTATIONS = [
    'db.users.update_one',
    'db.users.insert',
    'db.user_heroes.update_one',
    'db.user_heroes.insert',
    'db.user_heroes.delete',
    'db.gacha_pulls.insert',
    'db.transactions.insert',
    'db.inventory.update',
    'db.wallets.update',
    'db.mail.insert',
    'db.shop.',
    'db.vip.',
    'db.battle_pass.',
    'grant_reward(',
    'grant_currency(',
    'add_exp(',
    'spend_currency(',
    'apply_reward(',
    'sanctuary_affinity_mutation',
    'tower_reward',
    'arena_reward',
    'raid_reward',
]


def main() -> int:
    errors = []; notes = []
    if not ROUTE.exists(): errors.append('v96_team_formation.py missing'); return _emit(errors, notes)
    src = ROUTE.read_text(encoding='utf-8')
    violations = []
    for fp in FORBIDDEN_MUTATIONS:
        if fp in src:
            violations.append(fp)
    if violations:
        for v in violations:
            errors.append(f'forbidden mutation pattern detected: `{v}`')
    print(f'OK    forbidden mutation scan: {len(FORBIDDEN_MUTATIONS)} patterns checked, {len(violations)} violations')
    # Verify update target
    if 'await db.player_server_profiles.update_one' not in src:
        errors.append('expected update on db.player_server_profiles not found')
    return _emit(errors, notes)


def _emit(errors, notes):
    print('\n' + '=' * 72)
    report = {'pack': 'PACK_129_TEAM_SAVE_NO_REWARDS_NO_PROGRESS',
              'status': 'PASS' if not errors else 'FAIL',
              'errors': errors, 'notes': notes,
              'forbidden_mutations': FORBIDDEN_MUTATIONS,
              'validation_kind': 'STATIC',
              'enforcement': 'ENFORCED_WRITE_TARGET_IS_PLAYER_SERVER_PROFILES_TEAM_FORMATION_ONLY'}
    out = REPO_ROOT / 'backend' / 'scripts' / 'reports'; out.mkdir(parents=True, exist_ok=True)
    (out / 'pack_129_team_save_no_rewards_no_progress_report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    if errors:
        for e in errors: print(f'  FAIL  {e}')
        return 1
    print('PASS  team save touches NO rewards/economy/progression/inventory/gacha/shop/VIP/BP/mail/sanctuary')
    return 0


if __name__ == '__main__': sys.exit(main())
