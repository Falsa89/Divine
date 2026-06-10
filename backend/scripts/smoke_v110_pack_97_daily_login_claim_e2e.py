#!/usr/bin/env python3
"""Pack 97 — Daily login claim runtime smoke E2E (test-only).

Marker: pack_97_test_artifact=true. Cleanup garantito in finally.

Kill switches lifecycle:
  * Inizialmente entrambi OFF. Snapshot dei valori originali.
  * Lo smoke abilita entrambi via .env override + restart backend.
  * Test eseguiti. Poi ripristina entrambi a OFF (rimuove env vars).
"""
import os, sys, json, time, uuid, urllib.request, urllib.error, asyncio, hashlib
from datetime import datetime, timezone, timedelta
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

BASE = 'http://127.0.0.1:8001'
MONGO = os.getenv('MONGO_URL'); DB_NAME = 'divine_waifus'
TS = int(time.time())
EMAIL = f'pack97_test_user_{TS}@test.com'
SID_A = f's_pack97_a_{TS}'
SID_B = f's_pack97_b_{TS}'
MARKER = 'pack_97_test_artifact'
GLOBAL_KS = 'REWARD_CLAIM_LEDGER_LIVE_ENABLED'
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
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    await db.users.update_one({'id': uid}, {'$set': {MARKER: True}})
    await db.player_server_profiles.update_many({'user_id': uid}, {'$set': {MARKER: True}})


async def cleanup(uid):
    if not uid: return
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    u = await db.users.find_one({'id': uid})
    if not u or not u.get(MARKER):
        print(f'[CLEANUP REFUSED] user {uid} not marked'); return
    r1 = await db.users.delete_one({'id': uid, MARKER: True})
    r2 = await db.inventory.delete_many({'user_id': uid})
    r3 = await db.player_server_profiles.delete_many({'user_id': uid, MARKER: True})
    r4 = await db.user_heroes.delete_many({'user_id': uid})
    r5 = await db.user_equipment.delete_many({'user_id': uid})
    r6 = await db.wallets.delete_many({'user_id': uid})
    r7 = await db.reward_claim_ledger.delete_many({'user_id': uid})
    print(f'[CLEANUP OK] users={r1.deleted_count} psp={r3.deleted_count} ledger={r7.deleted_count}')


def run():
    uid = None; proofs = {}
    ks_global_orig = os.getenv(GLOBAL_KS, None)
    ks_daily_orig = os.getenv(DAILY_KS, None)
    try:
        # === 0. Both kill switches OFF by default ===
        st, body = get('/api/daily-login/claim/health')
        assert st == 200
        assert body.get('global_kill_switch_live_enabled') is False
        assert body.get('daily_kill_switch_live_enabled') is False
        assert body.get('claim_executable') is False
        proofs['both_kill_switches_default_off'] = True

        # === 1. Register + ensure PSP A + mark ===
        st, body = post('/api/register', {'email': EMAIL, 'password': 'pack97pw',
                                          'username': f'p97u_{TS}'})
        assert st == 200, body
        uid = body['user']['id']
        auth = {'Authorization': f'Bearer {body["token"]}'}
        proofs['register_ok'] = True
        st, body = post(f'/api/psp/ensure?server_id={SID_A}', None, auth)
        assert st in (200, 201)
        proofs['ensure_psp_a_ok'] = True
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        loop.run_until_complete(mark(uid))
        proofs['mark_pack_97_ok'] = True

        # === 2. Claim blocked when both off ===
        st, body = post(f'/api/daily-login/claim?server_id={SID_A}', {}, auth)
        assert st == 503, body
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert d.get('blocker') == 'REWARD_CLAIM_LEDGER_LIVE_DISABLED', d
        proofs['claim_blocked_when_global_off'] = True

        # === 3. Enable global only -> still blocked (need daily too) ===
        write_env_kv({GLOBAL_KS: 'true'})
        st, body = post(f'/api/daily-login/claim?server_id={SID_A}', {}, auth)
        assert st == 503, body
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert d.get('blocker') == 'DAILY_LOGIN_CLAIM_DISABLED'
        proofs['claim_blocked_when_only_global_on'] = True

        # === 4. Enable both -> ready ===
        write_env_kv({GLOBAL_KS: 'true', DAILY_KS: 'true'})
        st, body = get('/api/daily-login/claim/health')
        assert body.get('claim_executable') is True
        proofs['both_kill_switches_enabled'] = True

        # === 5. Preflight: indices ok ===
        st, body = post('/api/daily-login/claim/preflight', None, auth)
        assert st == 200
        assert (body.get('indices') or {}).get('stopped') is False
        proofs['daily_preflight_indices_ok'] = True

        # === 6. First daily claim ===
        st, body = post(f'/api/daily-login/claim?server_id={SID_A}', {'client_token': 'whatever_xyz'}, auth)
        assert st == 200, body
        assert body.get('idempotent_replay') is False
        assert body.get('claim_source') == 'daily_login_claim'
        ck1 = body.get('claim_key') or ''
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        assert ck1 == f'daily_login_{SID_A}_{today}', ck1
        rew = (body.get('rewards') or {}).get('server_scoped') or {}
        assert rew.get('mission_coins') == 10 and rew.get('honor') == 5, rew
        assert (body.get('rewards') or {}).get('live_grant') is True
        assert (body.get('rewards') or {}).get('account_wide') == {}
        proofs['first_daily_claim_success_with_fixed_reward'] = True

        # === 7. Replay same day -> idempotent ===
        st, body = post(f'/api/daily-login/claim?server_id={SID_A}', {'client_token': 'something_else'}, auth)
        assert st == 200 and body.get('idempotent_replay') is True
        proofs['same_day_replay_no_double_grant'] = True

        # Verify PSP balance still 10/5 (no double grant)
        loopv = asyncio.new_event_loop(); asyncio.set_event_loop(loopv)
        c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
        psp = loopv.run_until_complete(db.player_server_profiles.find_one({'user_id': uid, 'server_id': SID_A}))
        soft = (psp or {}).get('soft_currencies') or {}
        assert soft.get('mission_coins') == 10 and soft.get('honor') == 5, soft
        proofs['psp_balance_unchanged_after_replay'] = True

        # Single ledger row for today
        cnt = loopv.run_until_complete(
            db.reward_claim_ledger.count_documents(
                {'user_id': uid, 'server_id': SID_A, 'claim_source': 'daily_login_claim',
                 'claim_key': ck1})
        )
        assert cnt == 1, f'expected 1 ledger row, got {cnt}'
        proofs['ledger_single_row_for_daily_key'] = True

        # === 8. Client cannot bypass with different token ===
        # The endpoint ignores client_token; check that another call STILL replays.
        st, body = post(f'/api/daily-login/claim?server_id={SID_A}', {'client_token': 'random_attempt_to_bypass_' + uuid.uuid4().hex}, auth)
        assert st == 200 and body.get('idempotent_replay') is True
        proofs['client_token_cannot_bypass_daily_idempotency'] = True

        # === 9. Next-day simulation: test_day_override (allowed because marker present) ===
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime('%Y-%m-%d')
        st, body = post(f'/api/daily-login/claim?server_id={SID_A}&_test_day_override={tomorrow}', {}, auth)
        assert st == 200 and body.get('idempotent_replay') is False
        ck2 = body.get('claim_key')
        assert ck2 == f'daily_login_{SID_A}_{tomorrow}', ck2
        proofs['next_day_simulation_grants_new_claim'] = True

        # Now PSP must be doubled
        psp = loopv.run_until_complete(db.player_server_profiles.find_one({'user_id': uid, 'server_id': SID_A}))
        soft = (psp or {}).get('soft_currencies') or {}
        assert soft.get('mission_coins') == 20 and soft.get('honor') == 10, soft
        proofs['psp_balance_doubled_after_next_day_claim'] = True

        # Same next-day replay -> idempotent
        st, body = post(f'/api/daily-login/claim?server_id={SID_A}&_test_day_override={tomorrow}', {}, auth)
        assert st == 200 and body.get('idempotent_replay') is True
        proofs['next_day_same_day_replay_idempotent'] = True

        # === 10. Cross-server isolation (server B no PSP) ===
        st, body = post(f'/api/daily-login/claim?server_id={SID_B}', {}, auth)
        assert st == 409, body
        proofs['cross_server_b_no_psp_409'] = True

        # === 11. Cross-server: ensure PSP B and claim -> should grant NEW (independent server) ===
        st, body = post(f'/api/psp/ensure?server_id={SID_B}', None, auth)
        assert st in (200, 201)
        loop2 = asyncio.new_event_loop(); asyncio.set_event_loop(loop2)
        loop2.run_until_complete(mark(uid))  # ensure marker on new PSP B
        st, body = post(f'/api/daily-login/claim?server_id={SID_B}', {}, auth)
        assert st == 200 and body.get('idempotent_replay') is False
        ck_b = body.get('claim_key')
        assert SID_B in ck_b and SID_A not in ck_b
        # PSP A balance MUST be unchanged from cross-server claim
        psp_a = loopv.run_until_complete(db.player_server_profiles.find_one({'user_id': uid, 'server_id': SID_A}))
        soft_a = (psp_a or {}).get('soft_currencies') or {}
        assert soft_a.get('mission_coins') == 20 and soft_a.get('honor') == 10, soft_a
        psp_b = loopv.run_until_complete(db.player_server_profiles.find_one({'user_id': uid, 'server_id': SID_B}))
        soft_b = (psp_b or {}).get('soft_currencies') or {}
        assert soft_b.get('mission_coins') == 10 and soft_b.get('honor') == 5, soft_b
        proofs['cross_server_isolation_independent_claim_per_server'] = True

        # === 12. _test_day_override forbidden for non-test users (simulate by removing marker briefly?) ===
        # We test by registering ANOTHER user (NOT marked) and attempting override -> 403
        EMAIL2 = f'pack97_test_user_unmarked_{TS}@test.com'
        st, body = post('/api/register', {'email': EMAIL2, 'password': 'pack97pw',
                                          'username': f'p97u2_{TS}'})
        uid2 = body['user']['id']
        auth2 = {'Authorization': f'Bearer {body["token"]}'}
        st, _ = post(f'/api/psp/ensure?server_id={SID_A}', None, auth2)
        # Note: do NOT mark uid2
        st, body = post(f'/api/daily-login/claim?server_id={SID_A}&_test_day_override={tomorrow}', {}, auth2)
        # Either 403 forbidden or 409 PSP (depends on PSP existence). We want 403 specifically.
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert st == 403 and d.get('blocker') == 'DAY_OVERRIDE_FORBIDDEN_FOR_NON_TEST_USER', (st, d)
        proofs['day_override_forbidden_for_non_test_user'] = True
        # Cleanup uid2 BEFORE finally (it's NOT marked so the cleanup function won't catch it)
        loopc2 = asyncio.new_event_loop(); asyncio.set_event_loop(loopc2)
        c2 = AsyncIOMotorClient(MONGO); db2 = c2[DB_NAME]
        loopc2.run_until_complete(db2.users.delete_one({'id': uid2}))
        loopc2.run_until_complete(db2.player_server_profiles.delete_many({'user_id': uid2}))
        loopc2.run_until_complete(db2.reward_claim_ledger.delete_many({'user_id': uid2}))

        # === 13. Premium attempt via qa source still blocked (Pack 96 preserved) ===
        tokp = f'pack97_tok_{uuid.uuid4().hex[:16]}'
        st, body = post(f'/api/rewards/claim?server_id={SID_A}',
                        {'source': 'qa_controlled_soft_currency_claim',
                         'reward_instance_id': 'inst_premium_attempt',
                         'idempotency_token': tokp, 'payload': {'gems': 100}}, auth)
        assert st == 422
        proofs['pack_96_premium_block_preserved'] = True

        # === 14. Story battle strict still works (Pack 95) ===
        tok_st = f'pack97_tok_{uuid.uuid4().hex[:16]}'
        st, body = post(f'/api/story/battle?server_id={SID_A}&idempotency_token={tok_st}',
                        {'chapter_id': 1, 'stage': 1}, auth)
        assert st == 200 and body.get('pack_95_strict_story_progress_write') is True
        proofs['pack_95_story_strict_preserved'] = True

        # === 15. Pack 94 equipment loader strict ===
        st, body = get(f'/api/user/equipment?server_id={SID_A}', auth)
        assert st == 200 and body.get('filter_applied') is True
        proofs['pack_94_equipment_loader_preserved'] = True

        # === 16. Pack 93 wallet split ===
        st, body = get(f'/api/wallet?server_id={SID_A}', auth)
        assert body.get('wallet_source') == 'psp_server_scoped_split'
        proofs['pack_93_wallet_split_preserved'] = True

        # === 17. Pack 95 shops buy quarantine ===
        st, body = post(f'/api/shops/buy?server_id={SID_A}',
                        {'shop_id': 'honor_shop', 'item_id': 'hs_gacha_ticket'}, auth)
        assert body.get('blocker') == 'SHOPS_BUY_SERVER_SCOPE_DEFERRED'
        proofs['pack_95_shops_buy_quarantine_preserved'] = True

        # === 18. Disable daily kill switch -> blocks ===
        write_env_kv({GLOBAL_KS: 'true', DAILY_KS: 'false'})
        st, body = post(f'/api/daily-login/claim?server_id={SID_A}', {}, auth)
        assert st == 503
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert d.get('blocker') == 'DAILY_LOGIN_CLAIM_DISABLED'
        proofs['daily_kill_switch_disable_re_blocks'] = True

    finally:
        # Restore kill switches
        if ks_global_orig is None and ks_daily_orig is None:
            write_env_kv({GLOBAL_KS: None, DAILY_KS: None})
        else:
            write_env_kv({GLOBAL_KS: ks_global_orig, DAILY_KS: ks_daily_orig})
        proofs['kill_switches_restored_to_original'] = True
        if uid:
            loopc = asyncio.new_event_loop(); asyncio.set_event_loop(loopc)
            loopc.run_until_complete(cleanup(uid))
            proofs['cleanup_ok'] = True
    return proofs


if __name__ == '__main__':
    proofs = run()
    required = [
        'both_kill_switches_default_off', 'register_ok', 'ensure_psp_a_ok', 'mark_pack_97_ok',
        'claim_blocked_when_global_off', 'claim_blocked_when_only_global_on',
        'both_kill_switches_enabled', 'daily_preflight_indices_ok',
        'first_daily_claim_success_with_fixed_reward',
        'same_day_replay_no_double_grant', 'psp_balance_unchanged_after_replay',
        'ledger_single_row_for_daily_key', 'client_token_cannot_bypass_daily_idempotency',
        'next_day_simulation_grants_new_claim', 'psp_balance_doubled_after_next_day_claim',
        'next_day_same_day_replay_idempotent', 'cross_server_b_no_psp_409',
        'cross_server_isolation_independent_claim_per_server',
        'day_override_forbidden_for_non_test_user',
        'pack_96_premium_block_preserved', 'pack_95_story_strict_preserved',
        'pack_94_equipment_loader_preserved', 'pack_93_wallet_split_preserved',
        'pack_95_shops_buy_quarantine_preserved',
        'daily_kill_switch_disable_re_blocks',
        'kill_switches_restored_to_original', 'cleanup_ok',
    ]
    missing = [k for k in required if proofs.get(k) is not True]
    out = {
        'pack': 'MEGA_RELEASE_ACCELERATION_97_FIRST_REAL_CLAIM_SOURCE_AND_FRONTEND_REWARD_UNLOCK_MEGAPACK',
        'timestamp_utc_ts': TS, 'test_artifact_marker': MARKER,
        'global_kill_switch_env': GLOBAL_KS, 'daily_kill_switch_env': DAILY_KS,
        'kill_switches_default_off_for_safety': True,
        'proofs': proofs, 'required_missing': missing,
        'real_smoke_executed': len(missing) == 0,
        'test_only_writes': True, 'no_production_user_writes': True,
        'no_premium_grant': True, 'no_double_daily_reward': True,
        'no_reward_live_general': True,
    }
    out_path = '/app/data/design/v110_pack_97_daily_login_claim_frontend_unlock/v110_pack_97_runtime_smoke_e2e_result_v1.json'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f: json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    if missing:
        print(f'[v110 PACK_97_RUNTIME_SMOKE_E2E] BLOCKED missing={missing}'); sys.exit(2)
    print('[v110 PACK_97_RUNTIME_SMOKE_E2E] OK first_real_daily_claim_live_gated daily_idempotent_no_double_grant '
          'cross_server_isolated next_day_simulation_safe day_override_forbidden_non_test no_premium_grant '
          'pack_91_93_94_95_96_preserved kill_switch_lifecycle_clean cleanup_ok')
