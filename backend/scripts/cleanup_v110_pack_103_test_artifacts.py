#!/usr/bin/env python3
"""Pack 103 cleanup script."""
import os, sys, asyncio, argparse
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient
MARKER='pack_103_test_artifact'
KILL_SWITCHES=['TOWER_STRICT_EXECUTE_ENABLED','TOWER_FLOOR_CLAIM_ENABLED']
COLLECTIONS=['users','player_server_profiles','user_heroes','user_equipment','inventory','wallets','reward_claim_ledger','daily_quest_progress','tower_progress']

async def cleanup(apply):
    c=AsyncIOMotorClient(os.getenv('MONGO_URL'));db=c['divine_waifus']
    for col in COLLECTIONS:
        cnt = await db[col].count_documents({MARKER:True}) if col!='tower_progress' else 0
        if apply and cnt>0:
            r=await db[col].delete_many({MARKER:True}); print(f'  {col:30s} matched={cnt} deleted={r.deleted_count}'); continue
        print(f'  {col:30s} matched={cnt}')
    if not apply: print('\n[REFUSED BY DEFAULT] Re-run with --apply.')

def reset_kill_switches():
    env='/app/backend/.env'
    if not os.path.exists(env): return
    with open(env) as f: lines=f.readlines()
    new=[ln for ln in lines if not any(ln.startswith(f'{k}=') for k in KILL_SWITCHES)]
    if len(new)!=len(lines):
        with open(env,'w') as f: f.writelines(new); print(f'[KILL SWITCHES] Removed: {KILL_SWITCHES}')

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--apply',action='store_true'); p.add_argument('--reset-kill-switches',action='store_true')
    args=p.parse_args()
    if args.reset_kill_switches: reset_kill_switches()
    asyncio.run(cleanup(args.apply))
