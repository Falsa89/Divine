#!/usr/bin/env python3
"""Pack 89 cleanup script. Refuse-by-default. NO real production data touched."""
import os, sys, argparse, asyncio, re
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient
PATTERN=re.compile(r'^pack89_test_user_\d+@test\.com$')
async def main(apply_flag):
    c=AsyncIOMotorClient(os.getenv('MONGO_URL')); db=c.divine_waifus
    test_users=await db.users.find({'email':{'$regex':r'^pack89_test_user_\d+@test\.com$'}}).to_list(None)
    uids=[u['id'] for u in test_users]
    inv=await db.inventory.count_documents({'user_id':{'$in':uids}}) if uids else 0
    leak=await db.inventory.count_documents({'_slc_pack_89_test_leak':True})
    psp_q={'$or':[{'server_id':{'$regex':r'^s_pack89_'}},{'user_id':{'$in':uids}} if uids else {'user_id':'__never__'}]}
    psp=await db.player_server_profiles.count_documents(psp_q)
    print(f'test_users={len(uids)} test_inventory={inv} leak_marked={leak} test_psp={psp}')
    if not apply_flag: print('DRY-RUN. Use --apply.'); return 0
    total=len(uids)+inv+leak+psp
    if total==0: print('REFUSE: 0 targets'); return 0
    for u in test_users:
        if not PATTERN.match(u.get('email','')): print(f'REFUSE: {u.get("email")}'); return 1
    du=await db.users.delete_many({'id':{'$in':uids}})
    dinv=await db.inventory.delete_many({'$or':[{'user_id':{'$in':uids}} if uids else {'user_id':'__never__'},{'_slc_pack_89_test_leak':True}]})
    dpsp=await db.player_server_profiles.delete_many(psp_q)
    print(f'APPLIED: users={du.deleted_count} inv={dinv.deleted_count} psp={dpsp.deleted_count}')
    return 0
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--apply',action='store_true'); p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(); rc=asyncio.get_event_loop().run_until_complete(main(a.apply)); sys.exit(rc)
