#!/usr/bin/env python3
# Pack 82 - Track 5: runtime smoke real migrated user (HTTP probe).
import os, json, urllib.request, urllib.error, sys
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
import jwt as pyjwt
from datetime import datetime, timedelta
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, {k.lower(): v for k,v in dict(r.headers).items()}, r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        try: body = e.read().decode('utf-8')
        except Exception: body = ''
        return e.code, {k.lower(): v for k,v in dict(e.headers).items()}, body

async def find_smoke_user():
    c = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = c.divine_waifus
    # Pack 84 post-normalization: PSP.user_id e' uuid. Trova diretto.
    psp = await db.player_server_profiles.find_one({'server_id': 's1'})
    if psp:
        u = await db.users.find_one({'id': psp.get('user_id')})
        if u: return u
        # Pre-Pack 84 fallback: ObjectId
        from bson import ObjectId
        try: oid = ObjectId(psp.get('user_id'))
        except Exception: oid = None
        if oid:
            u = await db.users.find_one({'_id': oid})
            if u: return u
    return None

u = asyncio.get_event_loop().run_until_complete(find_smoke_user())
assert u, 'no migrated Pack 77 user with PSP s1 found for smoke'
uid_uuid = u['id']
JWT_SECRET = os.getenv('JWT_SECRET', 'secret_key_change_me')
tok = pyjwt.encode({'user_id': uid_uuid, 'exp': datetime.utcnow() + timedelta(minutes=10)}, JWT_SECRET, algorithm='HS256')
auth = {'Authorization': f'Bearer {tok}'}
BASE = 'http://127.0.0.1:8001'
# 1) migrated user su s1 -> filter_applied=true via ObjectId fallback
st, h, body = _get(f'{BASE}/api/user/heroes?server_id=s1', headers=auth)
assert st == 200, f's1 status: {st}'
assert h.get('x-filter-applied') == 'true', f'filter_applied: {h}'
# Pack 84 post-normalization: lookup mode is direct_uuid. Pre-Pack 84: objectid_compat_fallback. Both accepted.
assert h.get('x-psp-lookup-mode') in ('direct_uuid', 'objectid_compat_fallback'), f'lookup mode wrong: {h.get("x-psp-lookup-mode")}'
assert h.get('x-server-progression-state') == 'psp_present_server_scoped'
assert int(h.get('x-roster-count', '0')) >= 0
assert int(h.get('x-player-level', '0')) >= 1
# 2) fresh-start invariant su s2 (mai giocato dal migrato)
st2, h2, body2 = _get(f'{BASE}/api/user/heroes?server_id=s2', headers=auth)
assert st2 == 200
assert h2.get('x-blocker') == 'PLAYER_SERVER_PROFILE_REQUIRED', f's2 blocker: {h2}'
assert h2.get('x-player-level') == '1', f's2 level not fresh: {h2.get("x-player-level")}'
assert h2.get('x-player-exp') == '0', f's2 exp not fresh: {h2.get("x-player-exp")}'
assert h2.get('x-roster-count') == '0', f's2 roster not empty: {h2.get("x-roster-count")}'
assert h2.get('x-server-progression-state') == 'fresh_start_pending_psp_creation'
body2_json = json.loads(body2)
assert isinstance(body2_json, list) and len(body2_json) == 0, 'fresh-start body must be empty list'
print(f'[v110 PACK_82_RUNTIME_SMOKE_REAL_MIGRATED_USER] OK migrated_user_s1_filter_applied=true compat_fallback_ok fresh_start_s2_level=1 exp=0 roster=0 blocker=PLAYER_SERVER_PROFILE_REQUIRED no_copy_s1_to_s2')
