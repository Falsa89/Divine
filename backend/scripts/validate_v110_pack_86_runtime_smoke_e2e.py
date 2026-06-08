#!/usr/bin/env python3
import os, json, sys, urllib.request, asyncio, time
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
import jwt as pyjwt
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

BASE = 'http://127.0.0.1:8001'
MONGO = os.getenv('MONGO_URL')
JWT_SECRET = os.getenv('JWT_SECRET', 'secret_key_change_me')

def post_json(url, body, headers=None):
    h = {'Content-Type': 'application/json'}
    if headers: h.update(headers)
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=h, method='POST')
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, {k.lower(): v for k,v in dict(r.headers).items()}, json.loads(r.read())

def get_json(url, headers=None):
    h = {}
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, {k.lower(): v for k,v in dict(r.headers).items()}, json.loads(r.read())

async def cleanup(uid, sid):
    c = AsyncIOMotorClient(MONGO)
    db = c.divine_waifus
    await db.users.delete_one({'id': uid})
    await db.user_heroes.delete_many({'user_id': uid})
    await db.player_server_profiles.delete_many({'user_id': uid})
    await db.player_server_profiles.delete_one({'server_id': sid, '_slc_psp_created_by_pack': 'v110_pack_85_psp_onboarding_new_server_fresh_start'})

async def count_user_heroes(uid):
    c = AsyncIOMotorClient(MONGO)
    db = c.divine_waifus
    return await db.user_heroes.count_documents({'user_id': uid})

uid = None
NEW_SID = f's_pack86_e2e_{int(time.time())}'
email = f'pack86_test_user_{int(time.time())}@test.com'
try:
    # (1) register: must NOT create global starter user_heroes
    st, h, body = post_json(f'{BASE}/api/register', {'email': email, 'password': 'pwpack86test', 'username': 'pack86usr'})
    assert body.get('server_onboarding_required') is True, f'register response missing server_onboarding_required: {body}'
    assert body.get('starter_flow_required') is True
    assert body.get('starter_legacy_created_in_register') == 0, f'register MUST NOT create starter user_heroes: {body}'
    assert body.get('_slc_pack_86_register_starter_legacy_guard') is True
    uid = body['user']['id']
    token = body['token']
    # Verifica DB: 0 user_heroes
    actual_uh = asyncio.get_event_loop().run_until_complete(count_user_heroes(uid))
    assert actual_uh == 0, f'DB user_heroes for new register MUST be 0; got {actual_uh}'
    auth = {'Authorization': f'Bearer {token}'}
    # (2) ensure on new server
    st, h, body = post_json(f'{BASE}/api/psp/ensure?server_id={NEW_SID}', None, headers=auth)
    assert body.get('created') is True
    assert body.get('player_level') == 1
    assert body.get('player_exp') == 0
    assert body.get('no_cross_server_copy') is True
    # (3) post-ensure heroes
    st, h, body = get_json(f'{BASE}/api/user/heroes?server_id={NEW_SID}', headers=auth)
    assert h.get('x-filter-applied') == 'true'
    assert h.get('x-psp-lookup-mode') == 'direct_uuid'
    assert h.get('x-player-level') == '1'
    assert h.get('x-player-exp') == '0'
    assert isinstance(body, list) and len(body) == 0, f'roster MUST be empty fresh-start: {body}'
    # (4) post-ensure team
    st, h, body = get_json(f'{BASE}/api/team/get-formation?server_id={NEW_SID}', headers=auth)
    tf = body.get('team_formation') if isinstance(body, dict) else None
    assert tf == [] or tf is None or (isinstance(tf, list) and len(tf) == 0), f'team_formation MUST be empty: {tf}'
    # (5) idempotency
    st, h, body = post_json(f'{BASE}/api/psp/ensure?server_id={NEW_SID}', None, headers=auth)
    assert body.get('created') is False
    assert body.get('already_existed') is True
    assert h.get('x-psp-ensure-mode') == 'already_exists_no_write'
finally:
    if uid:
        asyncio.get_event_loop().run_until_complete(cleanup(uid, NEW_SID))
print('[v110 PACK_86_RUNTIME_SMOKE_E2E] OK register_no_global_starter ensure_fresh_start level=1 exp=0 heroes_filter_applied team_empty idempotent_re_ensure cleanup_executed')
