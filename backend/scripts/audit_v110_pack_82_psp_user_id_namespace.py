#!/usr/bin/env python3
# Pack 82 - PSP user_id namespace audit (READ-ONLY).
# NESSUNA scrittura DB. Conta PSP raggiungibili via direct uuid vs ObjectId fallback vs orphan.
import asyncio, os, sys, json
sys.path.insert(0, '/app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

async def main():
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
        if u:
            direct += 1
            continue
        if ObjectId is not None:
            try: oid = ObjectId(uid)
            except Exception: oid = None
            if oid:
                u2 = await db.users.find_one({'_id': oid})
                if u2:
                    compat += 1
                    continue
        orphan += 1
    out = {
        'psp_total': total,
        'direct_uuid_count': direct,
        'objectid_compat_fallback_count': compat,
        'orphan_count': orphan,
        'db_writes': 0,
        'read_only': True,
    }
    print(json.dumps(out, indent=2))
    return out

if __name__ == '__main__':
    asyncio.run(main())
