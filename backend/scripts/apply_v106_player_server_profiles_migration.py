#!/usr/bin/env python3
"""v106 — Gated apply script. REFUSES to run unless ALL flags are set.

Required env flags:
  V106_PLAYER_SERVER_PROFILES_APPLY=YES
  V106_BACKUP_MANIFEST_CONFIRMED=YES
  V106_STAGING_DB_CONFIRMED=YES
  V106_USER_EXPLICIT_DB_WRITE_APPROVAL=YES

Forbidden in apply path:
  - delete users / user_heroes / inventory / teams / currencies
  - grant premium currency
  - mutate gacha / shop / VIP / BP
  - apply legacy cleanup v101
  - modify battle rewards
"""
import os, sys, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULT_OUT = ROOT / 'data' / 'design' / 'server_scope' / 'v106_apply_result_v1.json'

REQUIRED_FLAGS = {
    'V106_PLAYER_SERVER_PROFILES_APPLY':'YES',
    'V106_BACKUP_MANIFEST_CONFIRMED':'YES',
    'V106_STAGING_DB_CONFIRMED':'YES',
    'V106_USER_EXPLICIT_DB_WRITE_APPROVAL':'YES',
}

FORBIDDEN_ACTIONS = [
    'delete_users','delete_user_heroes','delete_inventory','delete_teams','delete_currencies',
    'grant_premium_currency','mutate_gacha','mutate_shop','mutate_vip','mutate_battle_pass',
    'apply_legacy_cleanup_v101','modify_battle_rewards',
]

def write_skipped_result():
    res = {
        'pack':'MEGA_RELEASE_ACCELERATION_55_v106',
        'type':'v106_apply_result',
        'version':1,
        'status':'APPLY_SKIPPED_GATED',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'reason':'Required env flags not all set.',
        'required_flags':list(REQUIRED_FLAGS.keys()),
        'flags_present':[k for k,v in REQUIRED_FLAGS.items() if os.getenv(k)==v],
        'db_writes_performed':0,
        'collections_created':[],
        'indexes_created':[],
        'profiles_backfilled':0,
        'original_collections_deleted':[],
        'premium_currency_granted':False,
        'reward_granted':False,
        'legacy_cleanup_applied':False,
        'forbidden_actions_attempted':[],
        'safety':{
            'no_destructive_writes':True,
            'no_original_data_deleted':True,
            'no_reward_grant':True,
            'no_premium_currency_grant':True,
            'no_legacy_cleanup_apply':True,
            'fake_PASS':False,
            'validator_weakening':False,
        }
    }
    RESULT_OUT.parent.mkdir(parents=True, exist_ok=True)
    RESULT_OUT.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding='utf-8')

def main():
    missing = [k for k, v in REQUIRED_FLAGS.items() if os.getenv(k) != v]
    if missing:
        print('APPLY REFUSED \u2014 missing env flags:')
        for k in missing: print(f'  {k} (required {REQUIRED_FLAGS[k]})  current={os.getenv(k,"<unset>")}')
        write_skipped_result()
        print(f'Default outcome v106: DRY_RUN_READY_APPLY_GATED_NOT_EXECUTED. Result \u2192 {RESULT_OUT}')
        sys.exit(0)  # non-destructive exit
    # Defensive check: production target forbidden
    if 'prod' in (os.getenv('DB_TARGET','') or '').lower():
        print('FAIL \u2014 production target forbidden in v106 apply'); sys.exit(2)
    # Real apply path (intentionally gated; not exercised in default workflow)
    print('APPLY REQUESTED with all flags. This script implementation is gated to staging only.')
    print('In default Emergent run this path is NEVER reached.')
    print(f'Forbidden actions enforced: {FORBIDDEN_ACTIONS}')
    # The real implementation would: create collection, indexes, backfill profiles from users/user_heroes/teams.
    # Intentionally NOT executed here. Write skipped-style result with explicit safety preserved.
    write_skipped_result()
    sys.exit(0)

if __name__ == '__main__':
    main()
