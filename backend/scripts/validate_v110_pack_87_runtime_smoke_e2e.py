#!/usr/bin/env python3
import os, json, sys, urllib.request, asyncio, time
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

BASE = 'http://127.0.0.1:8001'
MONGO = os.getenv('MONGO_URL')

def post_json(url, body, headers=None):
    h = {'Content-Type': 'application/json'}
    if headers: h.update(headers)
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=h, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, {k.lower(): v for k,v in dict(r.headers).items()}, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), json.loads(e.read())

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

async def get_user_heroes(uid):
    c = AsyncIOMotorClient(MONGO)
    db = c.divine_waifus
    return await db.user_heroes.find({'user_id': uid}).to_list(None)

uid = None
SID = f's_pack87_e2e_{int(time.time())}'
email = f'pack87_test_user_{int(time.time())}@test.com'
try:
    st, h, body = post_json(f'{BASE}/api/register', {'email': email, 'password': 'pwpack87test', 'username': 'pack87u'})
    assert body.get('starter_legacy_created_in_register') == 0
    uid = body['user']['id']
    token = body['token']
    auth = {'Authorization': f'Bearer {token}'}
    # Ensure
    st, h, body = post_json(f'{BASE}/api/psp/ensure?server_id={SID}', None, headers=auth)
    assert body.get('created') is True
    assert body.get('player_level') == 1
    assert body.get('player_exp') == 0
    # Starter claim first time
    st, h, body = post_json(f'{BASE}/api/psp/starter/claim?server_id={SID}', None, headers=auth)
    assert body.get('v110_starter_claim') is True, f'starter claim failed: {body}'
    assert body.get('created') is True
    assert body.get('starter_user_heroes_created_now') == 3
    assert body.get('team_initialized') is True
    assert body.get('no_account_wide_starter') is True
    assert body.get('no_premium_grant') is True
    assert body.get('no_reward_grant') is True
    assert body.get('no_player_level_mutation') is True
    assert body.get('no_cross_server_copy') is True
    assert body.get('creation_source') == 'server_scoped_starter_flow_pack_87'
    assert h.get('x-starter-claim-mode') == 'starter_claimed_first_time'
    starter_uh_ids = body.get('starter_user_hero_ids', [])
    assert len(starter_uh_ids) == 3
    # Verify DB: tutti user_heroes hanno server_id + creation_source
    user_heroes_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(user_heroes_loop)
    user_heroes = user_heroes_loop.run_until_complete(get_user_heroes(uid))
    assert len(user_heroes) == 3
    for uh in user_heroes:
        assert uh.get('server_id') == SID, f'user_hero missing/wrong server_id: {uh}'
        assert uh.get('creation_source') == 'server_scoped_starter_flow_pack_87'
        assert uh.get('level') == 1
        assert uh.get('experience') == 0
    # GET /api/user/heroes?server_id=<SID>
    st, h, body = get_json(f'{BASE}/api/user/heroes?server_id={SID}', headers=auth)
    assert h.get('x-filter-applied') == 'true'
    assert h.get('x-psp-lookup-mode') == 'direct_uuid'
    assert isinstance(body, list) and len(body) == 3
    # Team formation
    st, h, body = get_json(f'{BASE}/api/team/get-formation?server_id={SID}', headers=auth)
    tf = body.get('team_formation') if isinstance(body, dict) else None
    # Pack 87: team initialized; expect non-empty
    assert isinstance(tf, list) and len(tf) == 3, f'expected team_formation with 3 starters, got: {tf}'
    # Idempotency: starter claim second call
    st, h, body = post_json(f'{BASE}/api/psp/starter/claim?server_id={SID}', None, headers=auth)
    assert body.get('created') is False
    assert body.get('already_claimed') is True
    assert body.get('starter_user_heroes_created_now') == 0
    assert h.get('x-starter-claim-mode') == 'already_claimed_no_write'
    # PSP missing su altro server (no auto-creation by claim)
    OTHER_SID = SID + '_other'
    st, h, body = post_json(f'{BASE}/api/psp/starter/claim?server_id={OTHER_SID}', None, headers=auth)
    assert body.get('blocker') == 'PLAYER_SERVER_PROFILE_REQUIRED', f'expected PSP required blocker on other server: {body}'
finally:
    if uid:
        loop2 = asyncio.new_event_loop()
        asyncio.set_event_loop(loop2)
        loop2.run_until_complete(cleanup(uid, SID))
print('[v110 PACK_87_RUNTIME_SMOKE_E2E] OK register_no_global_starter ensure_fresh_start starter_claim_first_3_created server_scoped user_heroes_team_initialized re_claim_idempotent psp_missing_blocker cleanup_executed')
