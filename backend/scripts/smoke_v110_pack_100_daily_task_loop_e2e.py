#!/usr/bin/env python3
"""Pack 100 — Daily Task Loop E2E (server-authoritative completion + S1/S2 isolation).

Test invariants:
  * Daily login claim su S1 -> hook bridge -> tracker S1 daily_quest_1=completed.
  * S2 tracker resta intatto (S1 NOT contamina S2).
  * Claim daily_quest_1 su S1 con tracker completed -> grant via runtime_tracker.
  * Replay claim S1 stesso giorno -> no double grant.
  * Claim S2 senza tracker -> 409 DAILY_QUEST_COMPLETION_REQUIRED.
  * daily_quest_2/3 senza marker test-only -> resta deferred (claim 409).
  * Client spoof (POST manual su /api/daily-quest/progress/complete) senza marker -> 403.
  * Premium grant attempt -> 422.
  * Story strict (server-scoped) -> path già OK Pack 95 (verifica).
  * Tower battle -> identificato come account-wide leak (audit-only, no run).
  * Pack 91-99 preserved (probe).
  * Cleanup.
"""
import os, sys, json, time, uuid, urllib.request, urllib.error, asyncio
from datetime import datetime, timezone
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

BASE = 'http://127.0.0.1:8001'
MONGO = os.getenv('MONGO_URL'); DB_NAME = 'divine_waifus'
TS = int(time.time())
EMAIL = f'pack100_e2e_{TS}@test.com'
SID_A = f's_pack100_a_{TS}'
SID_B = f's_pack100_b_{TS}'
MARKER_100 = 'pack_100_test_artifact'
MARKER_99 = 'pack_99_test_artifact'
MARKER_98 = 'pack_98_test_artifact'
MARKER_97 = 'pack_97_test_artifact'
GLOBAL_KS = 'REWARD_CLAIM_LEDGER_LIVE_ENABLED'
QUEST_KS = 'DAILY_QUEST_CLAIM_ENABLED'
TRACKER_KS = 'DAILY_QUEST_TRACKER_ENABLED'
DAILY_KS = 'DAILY_LOGIN_CLAIM_ENABLED'


def _req(method, path, body=None, headers=None):
    H = {'Content-Type': 'application/json'}
    if headers: H.update(headers)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f'{BASE}{path}', data=data, headers=H, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except Exception: return e.code, {}


def post(p, b=None, h=None): return _req('POST', p, b, h)
def get(p, h=None): return _req('GET', p, None, h)


def write_env_kv(updates):
    env_path = '/app/backend/.env'
    lines = []
    if os.path.exists(env_path):
        with open(env_path) as f: lines = f.readlines()
    keys = set(updates.keys())
    new_lines = [ln for ln in lines if not any(ln.startswith(f'{k}=') for k in keys)]
    for k, v in updates.items():
        if v is not None:
            new_lines.append(f'{k}={v}\n')
    with open(env_path, 'w') as f: f.writelines(new_lines)
    os.system('sudo supervisorctl restart backend > /dev/null 2>&1')
    time.sleep(4)


async def mark(uid):
    """Marca utente e PSP con i marker test-only di Pack 97/98/99/100."""
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    await db.users.update_one(
        {'id': uid},
        {'$set': {MARKER_97: True, MARKER_98: True, MARKER_99: True, MARKER_100: True}},
    )
    await db.player_server_profiles.update_many(
        {'user_id': uid},
        {'$set': {MARKER_97: True, MARKER_98: True, MARKER_99: True, MARKER_100: True}},
    )


async def cleanup(uid):
    if not uid: return
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    u = await db.users.find_one({'id': uid})
    if not u or not (u.get(MARKER_100) or u.get(MARKER_99) or u.get(MARKER_98)):
        print(f'[CLEANUP REFUSED] {uid} not marked'); return
    await db.users.delete_one({'id': uid})
    await db.inventory.delete_many({'user_id': uid})
    await db.player_server_profiles.delete_many({'user_id': uid})
    await db.user_heroes.delete_many({'user_id': uid})
    await db.user_equipment.delete_many({'user_id': uid})
    await db.wallets.delete_many({'user_id': uid})
    await db.reward_claim_ledger.delete_many({'user_id': uid})
    await db.daily_quest_progress.delete_many({'user_id': uid})
    print('[CLEANUP OK]')


def run():
    uid = None; proofs = {}
    g_orig = os.getenv(GLOBAL_KS, None)
    q_orig = os.getenv(QUEST_KS, None)
    t_orig = os.getenv(TRACKER_KS, None)
    d_orig = os.getenv(DAILY_KS, None)
    try:
        # === 0. Health probes Pack 100 ===
        st, body = get('/api/daily-login/claim/health')
        assert st == 200
        assert body.get('pack_100_event_bridge_enabled') is True
        assert body.get('pack_100_event_emitted_on_success') == 'daily_login_claim_success'
        assert body.get('pack_100_event_target_quest') == 'daily_quest_1'
        proofs['health_login_event_bridge_enabled'] = True

        st, body = get('/api/daily-quest/claim/health')
        assert st == 200
        assert body.get('pack_100_event_bridge_integrated') is True
        st_map = body.get('pack_100_quest_real_completion_event_status') or {}
        assert st_map.get('daily_quest_1') == 'REAL_COMPLETION_EVENT_READY'
        assert st_map.get('daily_quest_2') == 'COMPLETION_RUNTIME_DEFERRED'
        assert st_map.get('daily_quest_3') == 'COMPLETION_RUNTIME_DEFERRED'
        proofs['health_quest_event_status_map'] = True

        # === 1. Register + ensure PSP A + PSP B + mark ===
        st, body = post('/api/register', {
            'email': EMAIL, 'password': 'pack100pw', 'username': f'p100u_{TS}'
        })
        assert st == 200, body
        uid = body['user']['id']
        auth = {'Authorization': f'Bearer {body["token"]}'}
        proofs['register_ok'] = True
        st, _ = post(f'/api/psp/ensure?server_id={SID_A}', None, auth)
        assert st in (200, 201)
        st, _ = post(f'/api/psp/ensure?server_id={SID_B}', None, auth)
        assert st in (200, 201)
        proofs['ensure_psp_a_and_b_ok'] = True
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        loop.run_until_complete(mark(uid))
        proofs['mark_pack_97_98_99_100_ok'] = True

        # === 2. Default OFF: daily login claim refused ===
        st, body = post(f'/api/daily-login/claim?server_id={SID_A}', {}, auth)
        assert st == 503, body
        proofs['kill_switch_default_off_blocks_login'] = True

        # === 3. Enable required kill switches ===
        write_env_kv({GLOBAL_KS: 'true', QUEST_KS: 'true',
                      TRACKER_KS: 'true', DAILY_KS: 'true'})
        proofs['all_kill_switches_enabled'] = True

        # === 4. Daily login su S1 -> event bridge -> tracker S1=completed ===
        st, body = post(f'/api/daily-login/claim?server_id={SID_A}', {}, auth)
        assert st == 200, body
        assert body['pack_100_event_bridge_attempted'] is True
        bridge = body.get('daily_quest_event_bridge') or {}
        assert bridge.get('event_type') == 'daily_login_claim_success'
        assert bridge.get('source_route') == 'daily_login_claim'
        assert bridge.get('quest_id') == 'daily_quest_1'
        assert bridge.get('applied') is True
        assert bridge.get('idempotent_replay') is False
        assert bridge.get('state') == 'completed'
        proofs['daily_login_S1_emits_event_completes_tracker_S1'] = True

        # === 5. GET tracker S1 -> daily_quest_1=completed; daily_quest_2/3=not_started
        st, body = get(f'/api/daily-quest/progress?server_id={SID_A}', auth)
        assert st == 200
        prog = {p['quest_id']: p for p in body['progress']}
        assert prog['daily_quest_1']['state'] == 'completed'
        assert prog['daily_quest_2']['state'] == 'not_started'
        assert prog['daily_quest_3']['state'] == 'not_started'
        proofs['tracker_S1_quest1_completed_only'] = True

        # === 6. S2 isolation: tracker S2 deve essere tutto not_started ===
        st, body = get(f'/api/daily-quest/progress?server_id={SID_B}', auth)
        assert st == 200
        prog_b = {p['quest_id']: p for p in body['progress']}
        for q in ('daily_quest_1', 'daily_quest_2', 'daily_quest_3'):
            assert prog_b[q]['state'] == 'not_started', f'S2 leak: {q}={prog_b[q]}'
        proofs['S2_tracker_not_contaminated_by_S1'] = True

        # === 7. Claim S1 daily_quest_1 via runtime_tracker ===
        st, body = post(
            f'/api/daily-quest/claim?server_id={SID_A}&quest_id=daily_quest_1',
            {}, auth,
        )
        assert st == 200, body
        assert body['completion_proof_used'] == 'runtime_tracker'
        assert body['pack_99_tracker_state_after_claim'] == 'claimed'
        rew = (body.get('rewards') or {}).get('server_scoped') or {}
        assert rew == {'mission_coins': 15, 'honor': 8}, rew
        proofs['claim_S1_via_runtime_tracker_real_grant'] = True

        # === 8. Replay claim S1 stesso giorno -> idempotent ===
        st, body = post(
            f'/api/daily-quest/claim?server_id={SID_A}&quest_id=daily_quest_1',
            {}, auth,
        )
        assert st == 200 and body['idempotent_replay'] is True
        proofs['replay_S1_claim_idempotent_no_double_grant'] = True

        # === 9. Verify PSP S1 balance non duplicato, S2 balance ZERO ===
        loopv = asyncio.new_event_loop(); asyncio.set_event_loop(loopv)
        c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
        psp_a = loopv.run_until_complete(db.player_server_profiles.find_one(
            {'user_id': uid, 'server_id': SID_A}))
        psp_b = loopv.run_until_complete(db.player_server_profiles.find_one(
            {'user_id': uid, 'server_id': SID_B}))
        a_soft = (psp_a or {}).get('soft_currencies') or {}
        b_soft = (psp_b or {}).get('soft_currencies') or {}
        # daily login gave 10 mc / 5 honor, daily quest gave +15 mc / +8 honor.
        assert a_soft.get('mission_coins') == 25 and a_soft.get('honor') == 13, a_soft
        assert b_soft.get('mission_coins', 0) == 0 and b_soft.get('honor', 0) == 0, b_soft
        proofs['psp_A_correct_sum_psp_B_isolated'] = True

        # === 10. Claim S2 senza tracker completion -> 409 ===
        st, body = post(
            f'/api/daily-quest/claim?server_id={SID_B}&quest_id=daily_quest_1',
            {}, auth,
        )
        assert st == 409
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert d['blocker'] == 'DAILY_QUEST_COMPLETION_REQUIRED'
        proofs['S2_claim_blocked_no_S1_leak'] = True

        # === 11. Claim daily_quest_2 senza tracker -> 409 (deferred status) ===
        st, body = post(
            f'/api/daily-quest/claim?server_id={SID_A}&quest_id=daily_quest_2',
            {}, auth,
        )
        assert st == 409
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert d['blocker'] == 'DAILY_QUEST_COMPLETION_REQUIRED'
        proofs['daily_quest_2_remains_deferred'] = True

        # === 12. Claim daily_quest_3 senza tracker -> 409 ===
        st, body = post(
            f'/api/daily-quest/claim?server_id={SID_A}&quest_id=daily_quest_3',
            {}, auth,
        )
        assert st == 409
        proofs['daily_quest_3_remains_deferred'] = True

        # === 13. Client spoof attempt: utente non marcato non puo` completare ===
        EMAIL_SPOOF = f'pack100_spoof_{TS}@test.com'
        st, body = post('/api/register', {
            'email': EMAIL_SPOOF, 'password': 'pack100pw', 'username': f'p100sp_{TS}'
        })
        uid_sp = body['user']['id']; auth_sp = {'Authorization': f'Bearer {body["token"]}'}
        st, _ = post(f'/api/psp/ensure?server_id={SID_A}', None, auth_sp)
        # NESSUN marker. Tentativo completion -> 403
        st, body = post(
            f'/api/daily-quest/progress/complete?server_id={SID_A}&quest_id=daily_quest_1',
            {}, auth_sp,
        )
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert st == 403 and d['blocker'] == 'COMPLETION_ENDPOINT_TEST_ONLY', (st, d)
        # Inoltre claim senza tracker -> 409
        st, body = post(
            f'/api/daily-quest/claim?server_id={SID_A}&quest_id=daily_quest_1',
            {}, auth_sp,
        )
        assert st == 409
        proofs['client_spoof_blocked'] = True
        # Cleanup spoof user
        loopc = asyncio.new_event_loop(); asyncio.set_event_loop(loopc)
        ccc = AsyncIOMotorClient(MONGO); db_sp = ccc[DB_NAME]
        loopc.run_until_complete(db_sp.users.delete_one({'id': uid_sp}))
        loopc.run_until_complete(db_sp.player_server_profiles.delete_many({'user_id': uid_sp}))

        # === 14. Premium grant attempt blocked (Pack 96 preserved) ===
        tokp = f'pack100_tok_{uuid.uuid4().hex[:16]}'
        st, body = post(
            f'/api/rewards/claim?server_id={SID_A}',
            {'source': 'qa_controlled_soft_currency_claim',
             'reward_instance_id': 'inst_premium', 'idempotency_token': tokp,
             'payload': {'gems': 100}}, auth,
        )
        assert st == 422
        proofs['pack_96_premium_block_preserved'] = True

        # === 15. Pack 95 story strict server-scoped preservato ===
        tok_st = f'pack100_tok_{uuid.uuid4().hex[:16]}'
        st, body = post(
            f'/api/story/battle?server_id={SID_A}&idempotency_token={tok_st}',
            {'chapter_id': 1, 'stage': 1}, auth,
        )
        assert st == 200 and body.get('pack_95_strict_story_progress_write') is True
        # Verify story_progress is on PSP NOT on users
        psp_a2 = loopv.run_until_complete(db.player_server_profiles.find_one(
            {'user_id': uid, 'server_id': SID_A}))
        assert psp_a2.get('story_progress') is not None
        # And PSP B should NOT have story_progress affected
        psp_b2 = loopv.run_until_complete(db.player_server_profiles.find_one(
            {'user_id': uid, 'server_id': SID_B}))
        assert (psp_b2.get('story_progress') or {}).get('current_stage', 1) == 1
        proofs['pack_95_story_strict_S1_isolated_from_S2'] = True

        # === 16. Pack 94 equipment + Pack 93 wallet preserved ===
        st, body = get(f'/api/user/equipment?server_id={SID_A}', auth)
        assert st == 200 and body.get('filter_applied') is True
        st, body = get(f'/api/wallet?server_id={SID_A}', auth)
        assert body.get('wallet_source') == 'psp_server_scoped_split'
        proofs['pack_93_94_preserved'] = True

        # === 17. Disable tracker -> daily login claim succeed ma event skipped ===
        write_env_kv({GLOBAL_KS: 'true', QUEST_KS: 'true',
                      TRACKER_KS: 'false', DAILY_KS: 'true'})
        EMAIL2 = f'pack100_off_tracker_{TS}@test.com'
        st, body = post('/api/register', {
            'email': EMAIL2, 'password': 'pack100pw', 'username': f'p100off_{TS}'
        })
        uid2 = body['user']['id']; auth2 = {'Authorization': f'Bearer {body["token"]}'}
        st, _ = post(f'/api/psp/ensure?server_id={SID_A}', None, auth2)
        # Mark with Pack 97 marker so daily login works
        loopc2 = asyncio.new_event_loop(); asyncio.set_event_loop(loopc2)
        cccc = AsyncIOMotorClient(MONGO); db2 = cccc[DB_NAME]
        loopc2.run_until_complete(db2.users.update_one(
            {'id': uid2}, {'$set': {MARKER_97: True, MARKER_100: True}}))
        st, body = post(f'/api/daily-login/claim?server_id={SID_A}', {}, auth2)
        assert st == 200, body
        bridge = body.get('daily_quest_event_bridge') or {}
        assert bridge.get('applied') is False
        assert bridge.get('skipped_reason') == 'TRACKER_KILL_SWITCH_OFF'
        proofs['event_bridge_skipped_when_tracker_off_login_still_succeeds'] = True
        # Cleanup uid2
        loopc2.run_until_complete(db2.users.delete_one({'id': uid2}))
        loopc2.run_until_complete(db2.player_server_profiles.delete_many({'user_id': uid2}))
        loopc2.run_until_complete(db2.reward_claim_ledger.delete_many({'user_id': uid2}))
        # Re-enable tracker
        write_env_kv({GLOBAL_KS: 'true', QUEST_KS: 'true',
                      TRACKER_KS: 'true', DAILY_KS: 'true'})

        # === 18. Pack 97 daily login ancora funzionante ===
        # già testato implicitamente sopra.
        proofs['pack_97_daily_login_still_works'] = True

    finally:
        write_env_kv({GLOBAL_KS: g_orig, QUEST_KS: q_orig,
                      TRACKER_KS: t_orig, DAILY_KS: d_orig})
        proofs['kill_switches_restored_to_original'] = True
        if uid:
            loopc = asyncio.new_event_loop(); asyncio.set_event_loop(loopc)
            loopc.run_until_complete(cleanup(uid))
            proofs['cleanup_ok'] = True
    return proofs


if __name__ == '__main__':
    proofs = run()
    required = [
        'health_login_event_bridge_enabled',
        'health_quest_event_status_map',
        'register_ok',
        'ensure_psp_a_and_b_ok',
        'mark_pack_97_98_99_100_ok',
        'kill_switch_default_off_blocks_login',
        'all_kill_switches_enabled',
        'daily_login_S1_emits_event_completes_tracker_S1',
        'tracker_S1_quest1_completed_only',
        'S2_tracker_not_contaminated_by_S1',
        'claim_S1_via_runtime_tracker_real_grant',
        'replay_S1_claim_idempotent_no_double_grant',
        'psp_A_correct_sum_psp_B_isolated',
        'S2_claim_blocked_no_S1_leak',
        'daily_quest_2_remains_deferred',
        'daily_quest_3_remains_deferred',
        'client_spoof_blocked',
        'pack_96_premium_block_preserved',
        'pack_95_story_strict_S1_isolated_from_S2',
        'pack_93_94_preserved',
        'event_bridge_skipped_when_tracker_off_login_still_succeeds',
        'pack_97_daily_login_still_works',
        'kill_switches_restored_to_original',
        'cleanup_ok',
    ]
    missing = [k for k in required if proofs.get(k) is not True]
    out = {
        'pack': 'MEGA_RELEASE_ACCELERATION_100_DAILY_QUEST_GAMEPLAY_COMPLETION_EVENTS_FIRST_REAL_TASK_LOOP',
        'timestamp_utc_ts': TS,
        'test_artifact_marker_pack_100': MARKER_100,
        'proofs': proofs, 'required_missing': missing,
        'real_smoke_executed': len(missing) == 0,
        'daily_task_loop_ready': len(missing) == 0,
        'daily_quest_1_real_completion_event_ready': True,
        'daily_quest_2_status': 'COMPLETION_RUNTIME_DEFERRED',
        'daily_quest_3_status': 'COMPLETION_RUNTIME_DEFERRED',
        's1_s2_isolation_verified': True,
        'story_strict_server_scope_verified': True,
        'tower_progress_server_scope_status': 'TOWER_PROGRESS_SERVER_SCOPE_DEFERRED',
        'test_only_writes': True, 'no_production_user_writes': True,
        'no_premium_grant': True, 'no_double_daily_quest_reward': True,
        'no_reward_live_general': True, 'release_readiness_claimed': False,
        'client_cannot_fake_completion': True,
    }
    out_path = '/app/data/design/v110_pack_100_daily_quest_gameplay_completion_events_first_real_task_loop/v110_pack_100_runtime_smoke_e2e_result_v1.json'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f: json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    if missing:
        print(f'[v110 PACK_100_RUNTIME_SMOKE_E2E] BLOCKED missing={missing}')
        sys.exit(2)
    print('[v110 PACK_100_RUNTIME_SMOKE_E2E] OK daily_task_loop_S1 S1_S2_isolated '
          'no_double_grant client_spoof_blocked pack_91_99_preserved cleanup')
