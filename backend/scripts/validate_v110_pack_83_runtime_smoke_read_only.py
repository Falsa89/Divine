#!/usr/bin/env python3
# Pack 83 - Track J: runtime smoke read-only (Pack 82 dual-read still works).
import os, json, urllib.request, urllib.error, sys, asyncio
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
import jwt as pyjwt
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, {k.lower(): v for k,v in dict(r.headers).items()}, r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k,v in dict(e.headers).items()}, ''

async def find_user():
    c = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = c.divine_waifus
    from bson import ObjectId
    async for psp in db.player_server_profiles.find({'server_id': 's1'}).limit(50):
        uid = psp.get('user_id', '')
        try: oid = ObjectId(uid)
        except Exception: oid = None
        if not oid: continue
        u = await db.users.find_one({'_id': oid})
        if u: return u
    return None

u = asyncio.get_event_loop().run_until_complete(find_user())
assert u, 'no migrated user found for runtime smoke'
JWT_SECRET = os.getenv('JWT_SECRET', 'secret_key_change_me')
tok = pyjwt.encode({'user_id': u['id'], 'exp': datetime.utcnow() + timedelta(minutes=5)}, JWT_SECRET, algorithm='HS256')
auth = {'Authorization': f'Bearer {tok}'}
BASE = 'http://127.0.0.1:8001'
# Pack 82 dual-read s1 still works
st, h, _ = _get(f'{BASE}/api/user/heroes?server_id=s1', headers=auth)
assert st == 200
assert h.get('x-filter-applied') == 'true'
assert h.get('x-psp-lookup-mode') == 'objectid_compat_fallback'
assert h.get('x-server-progression-state') == 'psp_present_server_scoped'
# Fresh-start s2 still level=1 exp=0
st2, h2, _ = _get(f'{BASE}/api/user/heroes?server_id=s2', headers=auth)
assert st2 == 200
assert h2.get('x-blocker') == 'PLAYER_SERVER_PROFILE_REQUIRED'
assert h2.get('x-player-level') == '1'
assert h2.get('x-player-exp') == '0'
# No server_id deprecated
st3, h3, _ = _get(f'{BASE}/api/user/heroes', headers=auth)
assert st3 == 200
assert h3.get('x-server-scope') == 'account_wide_legacy_DEPRECATED'
assert h3.get('x-blocker') == 'SELECTED_SERVER_REQUIRED_FOR_PLAYER_FACING'
print('[v110 PACK_83_RUNTIME_SMOKE_READ_ONLY] OK pack82_dual_read_s1=filter_applied fresh_start_s2_level=1 no_server_id_deprecated db_writes=0')
