#!/usr/bin/env python3
import os, json, urllib.request, sys, asyncio
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
import jwt as pyjwt
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

async def find_user():
    c = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = c.divine_waifus
    psp = await db.player_server_profiles.find_one({'server_id': 's1', '_slc_psp_user_id_normalization_batch_id': {'$exists': True}})
    if not psp: return None
    return await db.users.find_one({'id': psp['user_id']})

u = asyncio.get_event_loop().run_until_complete(find_user())
assert u, 'no normalized PSP user found for runtime smoke'
JWT_SECRET = os.getenv('JWT_SECRET', 'secret_key_change_me')
tok = pyjwt.encode({'user_id': u['id'], 'exp': datetime.utcnow() + timedelta(minutes=5)}, JWT_SECRET, algorithm='HS256')
req = urllib.request.Request('http://127.0.0.1:8001/api/user/heroes?server_id=s1', headers={'Authorization': f'Bearer {tok}'})
with urllib.request.urlopen(req, timeout=20) as r:
    body = json.loads(r.read())
    h = {k.lower(): v for k,v in dict(r.headers).items()}
assert r.status == 200
assert h.get('x-psp-lookup-mode') == 'direct_uuid', f'post-normalization lookup mode must be direct_uuid, got {h.get("x-psp-lookup-mode")}'
assert h.get('x-filter-applied') == 'true'
assert h.get('x-server-progression-state') == 'psp_present_server_scoped'
assert int(h.get('x-player-level', '0')) >= 1
assert int(h.get('x-roster-count', '0')) >= 0
# Fresh-start s2 deve restare invariato
req2 = urllib.request.Request('http://127.0.0.1:8001/api/user/heroes?server_id=s2', headers={'Authorization': f'Bearer {tok}'})
with urllib.request.urlopen(req2, timeout=20) as r2:
    h2 = {k.lower(): v for k,v in dict(r2.headers).items()}
assert h2.get('x-blocker') == 'PLAYER_SERVER_PROFILE_REQUIRED'
assert h2.get('x-player-level') == '1'
assert h2.get('x-player-exp') == '0'
print('[v110 PACK_84_RUNTIME_SMOKE] OK post_normalization_lookup_mode=direct_uuid filter_applied=true fresh_start_s2_unchanged level=1 exp=0')
