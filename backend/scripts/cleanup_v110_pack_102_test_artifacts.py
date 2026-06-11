#!/usr/bin/env python3
"""Pack 102 cleanup script: rimuove artefatti marcati `pack_102_test_artifact`."""
import os, sys, asyncio, argparse
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

MARKER = 'pack_102_test_artifact'
KILL_SWITCHES = [
    'TOWER_STRICT_PREFLIGHT_ENABLED',
]
COLLECTIONS = [
    'users', 'player_server_profiles', 'user_heroes', 'user_equipment',
    'inventory', 'wallets', 'reward_claim_ledger', 'daily_quest_progress',
    'tower_progress',
]


async def cleanup(apply_mode: bool):
    c = AsyncIOMotorClient(os.getenv('MONGO_URL')); db = c['divine_waifus']
    for col in COLLECTIONS:
        cnt = await db[col].count_documents({MARKER: True}) if col != 'tower_progress' else 0
        if apply_mode and cnt > 0:
            r = await db[col].delete_many({MARKER: True})
            print(f"  {col:30s} matched={cnt} deleted={r.deleted_count}"); continue
        print(f"  {col:30s} matched={cnt}")
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
        print(f'[KILL SWITCHES] Removed: {KILL_SWITCHES}. Restart backend.')
    else:
        print('[KILL SWITCHES] Already at default OFF.')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--apply', action='store_true')
    p.add_argument('--reset-kill-switches', action='store_true')
    args = p.parse_args()
    if args.reset_kill_switches: reset_kill_switches()
    asyncio.run(cleanup(args.apply))
