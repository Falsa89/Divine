#!/usr/bin/env python3
"""v106 — Gated rollback script. REFUSES to run unless ALL flags are set.

Required env flags:
  V106_PLAYER_SERVER_PROFILES_ROLLBACK=YES
  V106_ROLLBACK_BACKUP_MANIFEST_CONFIRMED=YES

Forbidden during rollback:
  - delete unrecognized records
  - truncate users / user_heroes / inventory
  - grant premium currency
  - reward grant
"""
import os, sys, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN_OUT = ROOT / 'data' / 'design' / 'server_scope' / 'v106_rollback_plan_v1.json'

REQUIRED_FLAGS = {
    'V106_PLAYER_SERVER_PROFILES_ROLLBACK':'YES',
    'V106_ROLLBACK_BACKUP_MANIFEST_CONFIRMED':'YES',
}

FORBIDDEN = [
    'delete_unrecognized_records','truncate_users','truncate_user_heroes',
    'truncate_inventory','grant_premium_currency','reward_grant',
]

def main():
    missing = [k for k, v in REQUIRED_FLAGS.items() if os.getenv(k) != v]
    if missing:
        print('ROLLBACK REFUSED \u2014 missing env flags:')
        for k in missing: print(f'  {k} (required {REQUIRED_FLAGS[k]})  current={os.getenv(k,"<unset>")}')
        print(f'Plan documented at {PLAN_OUT}')
        sys.exit(0)
    print('ROLLBACK REQUESTED with all flags.')
    print('Strategy: reverse_via_backup_restore (preferred).')
    print('No unrecognized record deletion. No truncation.')
    print(f'Forbidden actions enforced: {FORBIDDEN}')
    print('Intentionally NOT executed in default Emergent run.')
    sys.exit(0)

if __name__ == '__main__':
    main()
