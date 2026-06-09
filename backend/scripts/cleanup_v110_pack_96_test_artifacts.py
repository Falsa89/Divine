#!/usr/bin/env python3
"""Pack 96 — cleanup test artifacts (refuse-by-default) + optional kill switch reset.

Usage:
  python3 cleanup_v110_pack_96_test_artifacts.py                 # DRY-RUN
  python3 cleanup_v110_pack_96_test_artifacts.py --apply         # esegue cancellazione
  python3 cleanup_v110_pack_96_test_artifacts.py --reset-kill-switch
"""
import os, sys, asyncio, argparse
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

MARKER = 'pack_96_test_artifact'
KILL_SWITCH_ENV = 'REWARD_CLAIM_LEDGER_LIVE_ENABLED'
COLLECTIONS = [
    'users', 'player_server_profiles', 'user_heroes',
    'user_equipment', 'inventory', 'wallets',
    'reward_claim_ledger',
]


async def cleanup(apply_mode: bool):
    mongo = os.getenv('MONGO_URL'); db_name = 'divine_waifus'
    c = AsyncIOMotorClient(mongo); db = c[db_name]
    report = {}
    for col in COLLECTIONS:
        cnt = await db[col].count_documents({MARKER: True})
        report[col] = {'matched': cnt, 'deleted': 0}
        if apply_mode and cnt > 0:
            r = await db[col].delete_many({MARKER: True})
            report[col]['deleted'] = r.deleted_count
    print('=' * 60)
    print(f"PACK 96 CLEANUP - {'APPLY' if apply_mode else 'DRY-RUN'} mode")
    print('=' * 60)
    for col, info in report.items():
        print(f"  {col:30s} matched={info['matched']:4d} deleted={info['deleted']:4d}")
    if not apply_mode:
        print('\n[REFUSED BY DEFAULT] Re-run with --apply to delete marked test artifacts.')
    else:
        print('\n[APPLIED] Pack 96 test artifacts removed.')


def reset_kill_switch():
    env_path = '/app/backend/.env'
    if not os.path.exists(env_path):
        print('[KILL SWITCH] .env not present, nothing to reset (default OFF).')
        return
    with open(env_path) as f:
        lines = f.readlines()
    new_lines = [ln for ln in lines if not ln.startswith(f'{KILL_SWITCH_ENV}=')]
    if len(new_lines) == len(lines):
        print('[KILL SWITCH] env var not set (default OFF). Nothing to remove.')
        return
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    print(f'[KILL SWITCH] Rimosso {KILL_SWITCH_ENV} da .env. Riavvia backend per applicare.')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--apply', action='store_true')
    p.add_argument('--reset-kill-switch', action='store_true')
    args = p.parse_args()
    if args.reset_kill_switch:
        reset_kill_switch()
    asyncio.run(cleanup(args.apply))
