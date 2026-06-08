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

async def inject_legacy_user_team(uid):
    c = AsyncIOMotorClient(MONGO); db = c.divine_waifus
    await db.users.update_one({'id': uid}, {'$set': {'team_formation': [{'slot_index': 0, 'user_hero_id': 'LEAK_TEST_HERO', '_legacy_account_wide_team_test': True}]}})

async def cleanup(uid):
    c = AsyncIOMotorClient(MONGO); db = c.divine_waifus
    await db.users.delete_one({'id': uid})
    await db.user_heroes.delete_many({'user_id': uid})
    await db.player_server_profiles.delete_many({'user_id': uid})

uid = None
TS = int(time.time())
SID = f's_pack88_e2e_{TS}'
OTHER_SID = f's_pack88_other_{TS}'
email = f'pack88_test_user_{TS}@test.com'
try:
    st, h, body = post_json(f'{BASE}/api/register', {'email': email, 'password': 'pwpack88', 'username': 'pack88u'})
    uid = body['user']['id']; token = body['token']
    auth = {'Authorization': f'Bearer {token}'}
    # Step 1: server_id presente, PSP missing -> blocker PLAYER_SERVER_PROFILE_REQUIRED
    st, h, body = get_json(f'{BASE}/api/team/get-formation?server_id={SID}', headers=auth)
    assert body.get('blocker') == 'PLAYER_SERVER_PROFILE_REQUIRED', f'step1 expected blocker PSP required: {body}'
    assert body.get('legacy_account_team_used') is False
    assert body.get('team_source') == 'none'
    assert body.get('pack_88_strict_server_scope') is True
    # Step 2: ensure
    post_json(f'{BASE}/api/psp/ensure?server_id={SID}', None, headers=auth)
    # Step 3: PSP exists, team empty -> PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER
    st, h, body = get_json(f'{BASE}/api/team/get-formation?server_id={SID}', headers=auth)
    assert body.get('blocker') == 'PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER', f'step3 expected blocker team not configured: {body}'
    assert body.get('legacy_account_team_used') is False
    assert body.get('team_source') == 'player_server_profile'
    assert body.get('team_formation') == []
    # Step 4: starter claim
    post_json(f'{BASE}/api/psp/starter/claim?server_id={SID}', None, headers=auth)
    # Step 5: team route returns 3 starters server-scoped
    st, h, body = get_json(f'{BASE}/api/team/get-formation?server_id={SID}', headers=auth)
    assert body.get('team_source') == 'player_server_profile'
    assert body.get('legacy_account_team_used') is False
    tf = body.get('team_formation', [])
    assert isinstance(tf, list) and len(tf) == 3, f'expected 3 starters, got {tf}'
    # Step 6: inietta user.team_formation legacy
    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    loop.run_until_complete(inject_legacy_user_team(uid))
    # Step 7: other server (no PSP) -> blocker, NO LEAK del legacy account-wide
    st, h, body = get_json(f'{BASE}/api/team/get-formation?server_id={OTHER_SID}', headers=auth)
    assert body.get('blocker') == 'PLAYER_SERVER_PROFILE_REQUIRED', f'step7 expected blocker on other server: {body}'
    assert body.get('legacy_account_team_used') is False, f'LEAK: legacy account-wide team appeared in other server: {body}'
    assert body.get('team_source') == 'none'
    assert body.get('team_formation') == []
    # Step 8: SID con team initialized: deve restituire ancora PSP team (NON legacy)
    st, h, body = get_json(f'{BASE}/api/team/get-formation?server_id={SID}', headers=auth)
    assert body.get('team_source') == 'player_server_profile'
    assert body.get('legacy_account_team_used') is False
    assert len(body.get('team_formation', [])) == 3
    # Verify each user_hero_id is starter (no LEAK_TEST_HERO)
    for entry in body.get('team_formation', []):
        assert entry.get('user_hero_id') != 'LEAK_TEST_HERO', f'LEAK detected: {entry}'
finally:
    if uid:
        loop2 = asyncio.new_event_loop(); asyncio.set_event_loop(loop2)
        loop2.run_until_complete(cleanup(uid))
print('[v110 PACK_88_RUNTIME_SMOKE_E2E] OK strict_server_scope_verified no_account_wide_leak_with_psp_missing no_account_wide_leak_with_starter_team_present blockers_explicit cleanup_executed')
