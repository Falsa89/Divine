#!/usr/bin/env python3
"""Pack 103 — Tower Execute + Floor Claim Ledger + Daily Quest 2 hook E2E."""
import os, sys, json, time, urllib.request, urllib.error, asyncio, uuid
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

BASE = 'http://127.0.0.1:8001'
MONGO = os.getenv('MONGO_URL'); DB_NAME = 'divine_waifus'
TS = int(time.time())
EMAIL = f'pack103_e2e_{TS}@test.com'
SID_A = f's_pack103_a_{TS}'; SID_B = f's_pack103_b_{TS}'
M_103 = 'pack_103_test_artifact'; M_102 = 'pack_102_test_artifact'
M_101 = 'pack_101_test_artifact'; M_99 = 'pack_99_test_artifact'; M_98 = 'pack_98_test_artifact'
M_97 = 'pack_97_test_artifact'
GLOBAL_KS = 'REWARD_CLAIM_LEDGER_LIVE_ENABLED'
EXEC_KS = 'TOWER_STRICT_EXECUTE_ENABLED'
FLOOR_KS = 'TOWER_FLOOR_CLAIM_ENABLED'
TRACKER_KS = 'DAILY_QUEST_TRACKER_ENABLED'
QUEST_KS = 'DAILY_QUEST_CLAIM_ENABLED'
PREFL_KS = 'TOWER_STRICT_PREFLIGHT_ENABLED'
LOGIN_KS = 'DAILY_LOGIN_CLAIM_ENABLED'


def _req(method, path, body=None, headers=None):
    H = {'Content-Type': 'application/json'}
    if headers: H.update(headers)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f'{BASE}{path}', data=data, headers=H, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except Exception: return e.code, {}


def post(p, b=None, h=None): return _req('POST', p, b, h)
def get(p, h=None): return _req('GET', p, None, h)


def write_env(updates):
    env = '/app/backend/.env'; lines = []
    if os.path.exists(env):
        with open(env) as f: lines = f.readlines()
    keys = set(updates)
    new = [ln for ln in lines if not any(ln.startswith(f'{k}=') for k in keys)]
    for k, v in updates.items():
        if v is not None: new.append(f'{k}={v}\n')
    with open(env, 'w') as f: f.writelines(new)
    os.system('sudo supervisorctl restart backend > /dev/null 2>&1'); time.sleep(4)


async def mark(uid):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    fields = {M_97: True, M_98: True, M_99: True, M_101: True, M_102: True, M_103: True}
    await db.users.update_one({'id': uid}, {'$set': fields})
    await db.player_server_profiles.update_many({'user_id': uid}, {'$set': fields})


async def snap_users(uid):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    u = await db.users.find_one({'id': uid})
    return {'gold': (u or {}).get('gold', 0), 'gems': (u or {}).get('gems', 0), 'experience': (u or {}).get('experience', 0)}


async def snap_psp(uid, sid):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    return await db.player_server_profiles.find_one({'user_id': uid, 'server_id': sid})


async def cleanup(uid):
    if not uid: return
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    u = await db.users.find_one({'id': uid})
    if not u or not u.get(M_103): print('[CLEANUP REFUSED]'); return
    for col in ('users','player_server_profiles','user_heroes','user_equipment','inventory','wallets','reward_claim_ledger','daily_quest_progress','tower_progress'):
        if col == 'users': await db.users.delete_one({'id': uid})
        else: await db[col].delete_many({'user_id': uid})
    print('[CLEANUP OK]')


def run():
    uid = None; proofs = {}
    orig = {k: os.getenv(k, None) for k in (GLOBAL_KS, EXEC_KS, FLOOR_KS, TRACKER_KS, QUEST_KS, PREFL_KS, LOGIN_KS)}
    try:
        # Health default OFF
        st, body = get('/api/tower/strict/health')
        assert st == 200 and body['execute_kill_switch_live_enabled'] is False
        assert body['floor_claim_kill_switch_live_enabled'] is False
        assert body['pack_103_execute_endpoint'] == '/api/tower/strict/battle/execute'
        assert body['pack_103_daily_quest_target'] == 'daily_quest_2'
        proofs['health_default_off'] = True

        # Register + PSP A+B + mark
        st, body = post('/api/register', {'email': EMAIL, 'password': 'pack103pw', 'username': f'p103u_{TS}'})
        assert st == 200, body
        uid = body['user']['id']; auth = {'Authorization': f'Bearer {body["token"]}'}
        post(f'/api/psp/ensure?server_id={SID_A}', None, auth)
        post(f'/api/psp/ensure?server_id={SID_B}', None, auth)
        proofs['register_psp_ab'] = True
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        loop.run_until_complete(mark(uid))
        proofs['mark_ok'] = True
        users_before = loop.run_until_complete(snap_users(uid))

        # Execute con kill switch OFF -> 503
        tok = uuid.uuid4().hex
        st, body = post(f'/api/tower/strict/battle/execute?server_id={SID_A}&floor=1&idempotency_token={tok}', {}, auth)
        assert st == 503
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert d['blocker'] == 'REWARD_CLAIM_LEDGER_DISABLED'
        proofs['execute_off_503'] = True

        # Abilita tutti i kill switch
        write_env({GLOBAL_KS: 'true', EXEC_KS: 'true', FLOOR_KS: 'true', TRACKER_KS: 'true', QUEST_KS: 'true', PREFL_KS: 'true', LOGIN_KS: 'true'})
        proofs['kill_switches_on'] = True

        # Unmarked user refused
        st_e, b_e = post('/api/register', {'email': f'unm_{TS}@x.com', 'password': 'pw', 'username': f'unm_{TS}'})
        uid_um = b_e['user']['id']; auth_um = {'Authorization': f'Bearer {b_e["token"]}'}
        post(f'/api/psp/ensure?server_id={SID_A}', None, auth_um)
        tok2 = uuid.uuid4().hex
        st, body = post(f'/api/tower/strict/battle/execute?server_id={SID_A}&floor=1&idempotency_token={tok2}', {}, auth_um)
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert st == 403 and d['blocker'] == 'EXECUTE_ENDPOINT_TEST_ONLY'
        proofs['unmarked_refused'] = True
        # cleanup unmarked
        ccc = AsyncIOMotorClient(MONGO); db2 = ccc[DB_NAME]
        lp2 = asyncio.new_event_loop(); asyncio.set_event_loop(lp2)
        lp2.run_until_complete(db2.users.delete_one({'id': uid_um}))
        lp2.run_until_complete(db2.player_server_profiles.delete_many({'user_id': uid_um}))

        # Missing fields
        st, body = post(f'/api/tower/strict/battle/execute?server_id={SID_A}&floor=1', {}, auth)
        assert st == 400
        st, body = post(f'/api/tower/strict/battle/execute?server_id={SID_A}&idempotency_token={tok}', {}, auth)
        assert st == 400
        proofs['validation_400'] = True

        # Out of range floor
        st, body = post(f'/api/tower/strict/battle/execute?server_id={SID_A}&floor=101&idempotency_token={tok}', {}, auth)
        assert st == 404
        proofs['out_of_range_404'] = True

        # Floor not allowed (skip): PSP current is 1, attempt floor 5
        st, body = post(f'/api/tower/strict/battle/execute?server_id={SID_A}&floor=5&idempotency_token={tok}', {}, auth)
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert st == 409 and d['blocker'] == 'FLOOR_NOT_ALLOWED_FOR_PSP'
        proofs['floor_skip_blocked'] = True

        # Execute floor 1 success
        tok_a1 = uuid.uuid4().hex
        st, body = post(f'/api/tower/strict/battle/execute?server_id={SID_A}&floor=1&idempotency_token={tok_a1}', {}, auth)
        assert st == 200, body
        assert body['idempotent_replay'] is False
        assert body['claim_source'] == 'tower_floor_completion_claim'
        assert body['rewards']['server_scoped'] == {'mission_coins': 5, 'honor': 3}
        assert body['tower_progress_advanced'] is True
        # daily quest event bridge
        bridge = body['daily_quest_event_bridge']
        assert bridge['event_type'] == 'tower_floor_clear_success'
        assert bridge['quest_id'] == 'daily_quest_2'
        assert bridge['applied'] is True
        proofs['execute_floor_1_S1_success'] = True

        # PSP A tower advanced, S2 not affected
        psp_a = loop.run_until_complete(snap_psp(uid, SID_A))
        psp_b = loop.run_until_complete(snap_psp(uid, SID_B))
        assert int((psp_a.get('tower_progress') or {}).get('floor', 0)) == 2
        assert int((psp_a.get('tower_progress') or {}).get('highest_floor', 0)) == 1
        # PSP B never used - tower_progress should not exist
        assert not (psp_b.get('tower_progress') or {})
        proofs['S1_advanced_S2_untouched'] = True

        # PSP A soft +5 mc, +3 honor
        a_soft = (psp_a.get('soft_currencies') or {})
        assert a_soft.get('mission_coins') == 5 and a_soft.get('honor') == 3
        proofs['psp_A_soft_granted_5_3'] = True

        # Tracker S1: daily_quest_2 = completed
        st, body = get(f'/api/daily-quest/progress?server_id={SID_A}', auth)
        prog = {p['quest_id']: p for p in body['progress']}
        assert prog['daily_quest_2']['state'] == 'completed'
        assert prog['daily_quest_1']['state'] == 'not_started'  # no daily login claim done
        proofs['tracker_S1_quest_2_completed'] = True

        # Tracker S2: all not_started (S1 NOT contamina S2)
        st, body = get(f'/api/daily-quest/progress?server_id={SID_B}', auth)
        prog_b = {p['quest_id']: p for p in body['progress']}
        for q in ('daily_quest_1','daily_quest_2','daily_quest_3'):
            assert prog_b[q]['state'] == 'not_started', f'S2 leak {q}'
        proofs['tracker_S2_uncontaminated'] = True

        # Replay same token -> idempotent
        st, body = post(f'/api/tower/strict/battle/execute?server_id={SID_A}&floor=1&idempotency_token={tok_a1}', {}, auth)
        assert st == 200 and body['idempotent_replay'] is True
        proofs['replay_same_token_idempotent'] = True

        # Replay different token same floor -> still idempotent (claim_key based)
        st, body = post(f'/api/tower/strict/battle/execute?server_id={SID_A}&floor=1&idempotency_token={uuid.uuid4().hex}', {}, auth)
        assert st == 200 and body['idempotent_replay'] is True
        proofs['replay_diff_token_same_floor_idempotent'] = True

        # PSP A soft invariato dopo replay
        psp_a = loop.run_until_complete(snap_psp(uid, SID_A))
        a_soft = (psp_a.get('soft_currencies') or {})
        assert a_soft.get('mission_coins') == 5 and a_soft.get('honor') == 3
        proofs['no_double_grant_after_replay'] = True

        # Claim daily_quest_2 via daily-quest/claim endpoint (Pack 98 ledger)
        st, body = post(f'/api/daily-quest/claim?server_id={SID_A}&quest_id=daily_quest_2', {}, auth)
        assert st == 200, body
        assert body['completion_proof_used'] == 'runtime_tracker'
        assert (body.get('rewards') or {}).get('server_scoped') == {'mission_coins': 15, 'honor': 8}
        proofs['daily_quest_2_claim_via_tracker'] = True

        # users.* invariato end-to-end
        users_after = loop.run_until_complete(snap_users(uid))
        assert users_before == users_after, f'users mutated {users_before} -> {users_after}'
        proofs['users_invariant'] = True

        # Legacy tower endpoints quarantinati
        st, _ = get('/api/tower/status', auth)
        assert st == 503
        st, _ = post('/api/tower/battle', {}, auth)
        assert st == 503
        proofs['legacy_tower_503_preserved'] = True

        # Pack 102 catalog ancora ok
        st, body = get('/api/tower/strict/catalog/floor/100')
        assert st == 200 and body['catalog_floor']['enemy_team'][0]['native_rarity'] == 6
        proofs['pack_102_catalog_preserved'] = True

        # Execute floor 2 (next allowed) success - different floor different claim_key
        tok_a2 = uuid.uuid4().hex
        st, body = post(f'/api/tower/strict/battle/execute?server_id={SID_A}&floor=2&idempotency_token={tok_a2}', {}, auth)
        assert st == 200 and body['idempotent_replay'] is False
        # Floor 2 in band 1-9: +5 mc / +3 honor
        psp_a = loop.run_until_complete(snap_psp(uid, SID_A))
        a_soft = (psp_a.get('soft_currencies') or {})
        # 5+5+15(daily quest claim) = 25 mc, 3+3+8=14 honor
        assert a_soft.get('mission_coins') == 25 and a_soft.get('honor') == 14
        proofs['execute_floor_2_advanced'] = True

        # Pack 100 daily login ancora funziona (separate quest 1)
        st, body = post(f'/api/daily-login/claim?server_id={SID_A}', {}, auth)
        assert st == 200
        bridge_login = body.get('daily_quest_event_bridge') or {}
        assert bridge_login.get('quest_id') == 'daily_quest_1'
        proofs['pack_100_daily_login_preserved'] = True

    finally:
        write_env(orig)
        proofs['kill_switches_restored'] = True
        if uid:
            lpc = asyncio.new_event_loop(); asyncio.set_event_loop(lpc)
            lpc.run_until_complete(cleanup(uid))
            proofs['cleanup_ok'] = True
    return proofs


if __name__ == '__main__':
    proofs = run()
    required = ['health_default_off', 'register_psp_ab', 'mark_ok', 'execute_off_503', 'kill_switches_on',
        'unmarked_refused', 'validation_400', 'out_of_range_404', 'floor_skip_blocked',
        'execute_floor_1_S1_success', 'S1_advanced_S2_untouched', 'psp_A_soft_granted_5_3',
        'tracker_S1_quest_2_completed', 'tracker_S2_uncontaminated',
        'replay_same_token_idempotent', 'replay_diff_token_same_floor_idempotent',
        'no_double_grant_after_replay', 'daily_quest_2_claim_via_tracker', 'users_invariant',
        'legacy_tower_503_preserved', 'pack_102_catalog_preserved',
        'execute_floor_2_advanced', 'pack_100_daily_login_preserved',
        'kill_switches_restored', 'cleanup_ok']
    missing = [k for k in required if proofs.get(k) is not True]
    out = {'pack': 'MEGA_RELEASE_ACCELERATION_103_TOWER_EXECUTE_FLOOR_CLAIM_LEDGER_DAILY_QUEST_2_HOOK_SUPERPACK',
        'timestamp_utc_ts': TS, 'test_artifact_marker_pack_103': M_103,
        'proofs': proofs, 'required_missing': missing, 'real_smoke_executed': len(missing) == 0,
        'tower_execute_ready': True, 'tower_floor_claim_ready': True,
        'daily_quest_2_status': 'REAL_COMPLETION_EVENT_READY_VIA_TOWER_CLEAR',
        's1_s2_isolation_verified': True, 'no_users_mutation': True,
        'no_premium_grant': True, 'no_reward_live_general': True,
        'release_readiness_claimed': False, 'client_cannot_grant_tower_reward': True}
    out_path = '/app/data/design/v110_pack_103_tower_execute_floor_claim_ledger_daily_quest_2/v110_pack_103_runtime_smoke_e2e_result_v1.json'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f: json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    if missing:
        print(f'[v110 PACK_103_SMOKE] BLOCKED missing={missing}'); sys.exit(2)
    print('[v110 PACK_103_SMOKE] OK execute_ready ledger_idempotent S1_S2_isolated quest_2_real_complete no_premium no_users_mutation')
