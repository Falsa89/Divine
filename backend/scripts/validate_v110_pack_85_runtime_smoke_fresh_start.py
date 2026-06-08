#!/usr/bin/env python3
import os, json, sys, urllib.request, asyncio
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
import jwt as pyjwt
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

async def find_u():
    c = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = c.divine_waifus
    psp = await db.player_server_profiles.find_one({'server_id': 's1'})
    return await db.users.find_one({'id': psp['user_id']})

async def cleanup(uid, sid):
    c = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = c.divine_waifus
    return await db.player_server_profiles.delete_one({'user_id': uid, 'server_id': sid, '_slc_psp_created_by_pack': 'v110_pack_85_psp_onboarding_new_server_fresh_start'})

u = asyncio.get_event_loop().run_until_complete(find_u())
JWT_SECRET = os.getenv('JWT_SECRET', 'secret_key_change_me')
tok = pyjwt.encode({'user_id': u['id'], 'exp': datetime.utcnow() + timedelta(minutes=10)}, JWT_SECRET, algorithm='HS256')
auth = {'Authorization': f'Bearer {tok}'}
NEW_SID = f's_pack85_val_{int(datetime.utcnow().timestamp())}'

def post(url):
    req = urllib.request.Request(url, headers=auth, method='POST')
    with urllib.request.urlopen(req, timeout=20) as r: return r.status, {k.lower(): v for k,v in dict(r.headers).items()}, json.loads(r.read())
def get(url):
    req = urllib.request.Request(url, headers=auth)
    with urllib.request.urlopen(req, timeout=20) as r: return r.status, {k.lower(): v for k,v in dict(r.headers).items()}, json.loads(r.read())

BASE = 'http://127.0.0.1:8001'
try:
    # 1) pre-ensure -> blocker
    st, h, body = get(f'{BASE}/api/user/heroes?server_id={NEW_SID}')
    assert h.get('x-blocker') == 'PLAYER_SERVER_PROFILE_REQUIRED'
    assert len(body) == 0
    # 2) ensure -> created
    st, h, body = post(f'{BASE}/api/psp/ensure?server_id={NEW_SID}')
    assert body.get('created') is True
    assert body.get('player_level') == 1
    assert body.get('player_exp') == 0
    assert body.get('no_cross_server_copy') is True
    assert h.get('x-psp-ensure-mode') == 'fresh_start_created'
    # 3) post-ensure -> filter_applied=true, level=1, roster=0
    st, h, body = get(f'{BASE}/api/user/heroes?server_id={NEW_SID}')
    assert h.get('x-filter-applied') == 'true'
    assert h.get('x-psp-lookup-mode') == 'direct_uuid'
    assert h.get('x-player-level') == '1'
    assert h.get('x-player-exp') == '0'
    assert len(body) == 0
    # 4) re-ensure idempotent
    st, h, body = post(f'{BASE}/api/psp/ensure?server_id={NEW_SID}')
    assert body.get('created') is False
    assert body.get('already_existed') is True
    assert h.get('x-psp-ensure-mode') == 'already_exists_no_write'
    # 5) s1 ancora intatto
    st, h, body = get(f'{BASE}/api/user/heroes?server_id=s1')
    assert int(h.get('x-player-level', '0')) >= 1
    assert h.get('x-filter-applied') == 'true'
finally:
    asyncio.get_event_loop().run_until_complete(cleanup(u['id'], NEW_SID))
print('[v110 PACK_85_RUNTIME_SMOKE_FRESH_START] OK pre_blocker ensure_creates_fresh post_filter_applied=true level=1 exp=0 roster=0 re_ensure_idempotent s1_unchanged')
