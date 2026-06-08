#!/usr/bin/env python3
import os, json, asyncio, sys
sys.path.insert(0, '/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

async def audit():
    c = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = c.divine_waifus
    total = await db.player_server_profiles.count_documents({})
    direct = 0; compat = 0; orphan = 0
    try:
        from bson import ObjectId
    except ImportError:
        ObjectId = None
    async for psp in db.player_server_profiles.find({}):
        uid = psp.get('user_id', '')
        u = await db.users.find_one({'id': uid})
        if u: direct += 1; continue
        if ObjectId is not None:
            try: oid = ObjectId(uid)
            except Exception: oid = None
            if oid and await db.users.find_one({'_id': oid}): compat += 1; continue
        orphan += 1
    return total, direct, compat, orphan

total, direct, compat, orphan = asyncio.get_event_loop().run_until_complete(audit())
assert total == 1690, f'psp total mismatch: {total}'
assert direct == 1690, f'direct_uuid post-execute must be 1690; got {direct}'
assert compat == 0, f'objectid_compat_fallback post-execute must be 0; got {compat}'
assert orphan == 0, f'orphan must remain 0; got {orphan}'
print(f'[v110 PACK_84_POST_NAMESPACE_AUDIT] OK total={total} direct={direct} compat={compat} orphan=0 target_post_execute_MET')
