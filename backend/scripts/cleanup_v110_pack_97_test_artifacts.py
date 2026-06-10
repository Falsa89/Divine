#!/usr/bin/env python3
"""Pack 97 — cleanup test artifacts (refuse-by-default) + kill switches reset."""
import os, sys, asyncio, argparse
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

MARKER = 'pack_97_test_artifact'
KILL_SWITCHES = ['REWARD_CLAIM_LEDGER_LIVE_ENABLED', 'DAILY_LOGIN_CLAIM_ENABLED']
COLLECTIONS = ['users', 'player_server_profiles', 'user_heroes', 'user_equipment',
               'inventory', 'wallets', 'reward_claim_ledger']


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
    print(f"PACK 97 CLEANUP - {'APPLY' if apply_mode else 'DRY-RUN'}")
    print('=' * 60)
    for col, info in report.items():
        print(f"  {col:30s} matched={info['matched']:4d} deleted={info['deleted']:4d}")
    if not apply_mode:
        print('\n[REFUSED BY DEFAULT] Re-run with --apply.')


def reset_kill_switches():
    env_path = '/app/backend/.env'
    if not os.path.exists(env_path):
        print('[KILL SWITCHES] .env not present.'); return
    with open(env_path) as f: lines = f.readlines()
    new_lines = [ln for ln in lines if not any(ln.startswith(f'{k}=') for k in KILL_SWITCHES)]
    if len(new_lines) != len(lines):
        with open(env_path, 'w') as f: f.writelines(new_lines)
        print(f'[KILL SWITCHES] Rimosse env: {KILL_SWITCHES}. Restart backend per applicare.')
    else:
        print('[KILL SWITCHES] Already at default OFF.')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--apply', action='store_true')
    p.add_argument('--reset-kill-switches', action='store_true')
    args = p.parse_args()
    if args.reset_kill_switches: reset_kill_switches()
    asyncio.run(cleanup(args.apply))
