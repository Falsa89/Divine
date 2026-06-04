#!/usr/bin/env python3
"""
v98 — Hard Delete Cron Dry-Run.
USAGE: python3 backend/scripts/cron_v98_hard_delete_dry_run.py
Scans users with pending_deletion=true AND scheduled_deletion_at < now.
If V98_HARD_DELETE_RUNTIME_ENABLED=true => executes hard delete (audit trail).
Default: dry-run, no DB mutations.
"""
import os, sys, asyncio
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,os.path.join(ROOT,'backend'))
import motor.motor_asyncio
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
MONGO_URL=os.getenv('MONGO_URL','mongodb://localhost:27017')
DB_NAME=os.getenv('DB_NAME','divine_waifus')
ENABLED=os.getenv('V98_HARD_DELETE_RUNTIME_ENABLED','false').lower()=='true'

async def main():
    client=motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db=client[DB_NAME]
    now=datetime.utcnow()
    candidates=db.users.find({'pending_deletion':True,'scheduled_deletion_at':{'$lt':now}})
    count=0; deleted=0
    async for u in candidates:
        count+=1
        print(f"candidate: user_id={u.get('id')} alias={u.get('alias')} scheduled={u.get('scheduled_deletion_at')}")
        if ENABLED:
            await db.refresh_tokens.delete_many({'user_id':u['id']})
            await db.users.delete_one({'id':u['id']})
            deleted+=1
    print(f'---')
    print(f'Total candidates: {count}')
    print(f'Hard-delete runtime: {"EXECUTED" if ENABLED else "DRY_RUN_NO_DB_MUTATION"}')
    print(f'Deleted: {deleted}')
    client.close()

if __name__=='__main__': asyncio.run(main())
