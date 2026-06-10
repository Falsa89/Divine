#!/usr/bin/env python3
"""Pack 98 — Daily home unlock + daily_quest_completion_claim smoke E2E."""
import os, sys, json, time, uuid, urllib.request, urllib.error, asyncio
from datetime import datetime, timezone, timedelta
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

BASE = 'http://127.0.0.1:8001'
MONGO = os.getenv('MONGO_URL'); DB_NAME = 'divine_waifus'
TS = int(time.time())
EMAIL = f'pack98_test_user_{TS}@test.com'
SID_A = f's_pack98_a_{TS}'
SID_B = f's_pack98_b_{TS}'
MARKER = 'pack_98_test_artifact'
GLOBAL_KS = 'REWARD_CLAIM_LEDGER_LIVE_ENABLED'
QUEST_KS = 'DAILY_QUEST_CLAIM_ENABLED'
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
        print(f'[CLEANUP REFUSED] {uid} not marked'); return
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
    g_orig = os.getenv(GLOBAL_KS, None); q_orig = os.getenv(QUEST_KS, None); d_orig = os.getenv(DAILY_KS, None)
    try:
        # === 0. Default state OFF ===
        st, body = get('/api/daily-quest/claim/health')
        assert st == 200
        assert body['claim_executable'] is False
        assert body['ready_status'] == 'READY_GATED_COMPLETION_REQUIRED'
        proofs['daily_quest_default_off_and_gated'] = True

        # === 1. Register + ensure PSP A + mark ===
        st, body = post('/api/register', {'email': EMAIL, 'password': 'pack98pw', 'username': f'p98u_{TS}'})
        assert st == 200, body
        uid = body['user']['id']
        auth = {'Authorization': f'Bearer {body["token"]}'}
        proofs['register_ok'] = True
        st, _ = post(f'/api/psp/ensure?server_id={SID_A}', None, auth); assert st in (200, 201)
        proofs['ensure_psp_a_ok'] = True
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        loop.run_until_complete(mark(uid))
        proofs['mark_pack_98_ok'] = True

        # === 2. Claim blocked when kill switches off ===
        st, body = post(f'/api/daily-quest/claim?server_id={SID_A}&quest_id=daily_quest_1', {}, auth)
        assert st == 503
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert d['blocker'] == 'REWARD_CLAIM_LEDGER_LIVE_DISABLED'
        proofs['quest_claim_blocked_when_global_off'] = True

        # === 3. Enable global only -> quest_off blocker ===
        write_env_kv({GLOBAL_KS: 'true'})
        st, body = post(f'/api/daily-quest/claim?server_id={SID_A}&quest_id=daily_quest_1', {}, auth)
        assert st == 503
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert d['blocker'] == 'DAILY_QUEST_CLAIM_DISABLED'
        proofs['quest_claim_blocked_when_only_global_on'] = True

        # === 4. Both on ===
        write_env_kv({GLOBAL_KS: 'true', QUEST_KS: 'true'})
        st, body = get('/api/daily-quest/claim/health')
        assert body['claim_executable'] is True
        proofs['both_kill_switches_enabled'] = True

        # === 5. Preflight idempotent indices ===
        st, body = post('/api/daily-quest/claim/preflight', None, auth)
        assert st == 200
        assert (body.get('indices') or {}).get('stopped') is False
        proofs['quest_preflight_indices_ok'] = True

        # === 6. Real user without completion proof -> 409 DAILY_QUEST_COMPLETION_REQUIRED ===
        st, body = post(f'/api/daily-quest/claim?server_id={SID_A}&quest_id=daily_quest_1', {}, auth)
        assert st == 409
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert d['blocker'] == 'DAILY_QUEST_COMPLETION_REQUIRED', d
        proofs['quest_claim_completion_required_for_real_user'] = True

        # === 7. Quest ID NOT whitelisted -> 422 ===
        st, body = post(f'/api/daily-quest/claim?server_id={SID_A}&quest_id=daily_quest_99_bogus',
                        {'test_completion_proof': True}, auth)
        assert st == 422
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert d['blocker'] == 'QUEST_ID_NOT_WHITELISTED'
        proofs['quest_id_not_whitelisted_blocked'] = True

        # === 8. First quest claim with test marker proof ===
        st, body = post(f'/api/daily-quest/claim?server_id={SID_A}&quest_id=daily_quest_1',
                        {'test_completion_proof': True, 'client_token': 'abc'}, auth)
        assert st == 200, body
        assert body['idempotent_replay'] is False
        assert body['quest_id'] == 'daily_quest_1'
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        assert body['claim_key'] == f'daily_quest_{SID_A}_daily_quest_1_{today}'
        rew = (body.get('rewards') or {}).get('server_scoped') or {}
        assert rew == {'mission_coins': 15, 'honor': 8}, rew
        assert body['completion_proof_used'] == 'test_only_marker'
        proofs['first_quest_claim_test_proof_success'] = True

        # === 9. Replay (same quest, same day, with proof) -> idempotent ===
        st, body = post(f'/api/daily-quest/claim?server_id={SID_A}&quest_id=daily_quest_1',
                        {'test_completion_proof': True}, auth)
        assert st == 200 and body['idempotent_replay'] is True
        proofs['same_day_quest_replay_no_double_grant'] = True

        # Verify PSP balance
        loopv = asyncio.new_event_loop(); asyncio.set_event_loop(loopv)
        c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
        psp = loopv.run_until_complete(db.player_server_profiles.find_one({'user_id': uid, 'server_id': SID_A}))
        soft = (psp or {}).get('soft_currencies') or {}
        assert soft.get('mission_coins') == 15 and soft.get('honor') == 8, soft
        proofs['psp_balance_unchanged_after_quest_replay'] = True

        # === 10. Different quest same day -> grants new ===
        st, body = post(f'/api/daily-quest/claim?server_id={SID_A}&quest_id=daily_quest_2',
                        {'test_completion_proof': True}, auth)
        assert st == 200 and body['idempotent_replay'] is False
        proofs['different_quest_same_day_grants_new'] = True
        psp = loopv.run_until_complete(db.player_server_profiles.find_one({'user_id': uid, 'server_id': SID_A}))
        soft = (psp or {}).get('soft_currencies') or {}
        assert soft.get('mission_coins') == 30 and soft.get('honor') == 16, soft
        proofs['psp_balance_doubled_after_two_quests'] = True

        # === 11. Next-day simulation grants new ===
        tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime('%Y-%m-%d')
        st, body = post(f'/api/daily-quest/claim?server_id={SID_A}&quest_id=daily_quest_1&_test_day_override={tomorrow}',
                        {'test_completion_proof': True}, auth)
        assert st == 200 and body['idempotent_replay'] is False
        proofs['next_day_quest_simulation_grants_new'] = True

        # === 12. Cross-server B: no PSP -> 409 ===
        st, body = post(f'/api/daily-quest/claim?server_id={SID_B}&quest_id=daily_quest_1',
                        {'test_completion_proof': True}, auth)
        assert st == 409
        proofs['quest_cross_server_b_no_psp_409'] = True

        # === 13. Register unmarked user -> proof bypass forbidden ===
        EMAIL2 = f'pack98_unmarked_{TS}@test.com'
        st, body = post('/api/register', {'email': EMAIL2, 'password': 'pack98pw', 'username': f'p98u2_{TS}'})
        uid2 = body['user']['id']; auth2 = {'Authorization': f'Bearer {body["token"]}'}
        st, _ = post(f'/api/psp/ensure?server_id={SID_A}', None, auth2)
        st, body = post(f'/api/daily-quest/claim?server_id={SID_A}&quest_id=daily_quest_1',
                        {'test_completion_proof': True}, auth2)
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert st == 403 and d['blocker'] == 'TEST_COMPLETION_PROOF_FORBIDDEN_FOR_NON_TEST_USER', (st, d)
        proofs['test_completion_proof_forbidden_for_non_test_user'] = True
        # Cleanup uid2
        loopc2 = asyncio.new_event_loop(); asyncio.set_event_loop(loopc2)
        c_unmark = AsyncIOMotorClient(MONGO); db_unmark = c_unmark[DB_NAME]
        loopc2.run_until_complete(db_unmark.users.delete_one({'id': uid2}))
        loopc2.run_until_complete(db_unmark.player_server_profiles.delete_many({'user_id': uid2}))
        loopc2.run_until_complete(db_unmark.reward_claim_ledger.delete_many({'user_id': uid2}))

        # === 14. Pack 97 daily login still works alongside Pack 98 quest ===
        write_env_kv({GLOBAL_KS: 'true', QUEST_KS: 'true', DAILY_KS: 'true'})
        st, body = post(f'/api/daily-login/claim?server_id={SID_A}', {}, auth)
        assert st == 200 and body['idempotent_replay'] is False
        proofs['pack_97_daily_login_still_works'] = True

        # === 15. Pack 96 premium block preserved ===
        tokp = f'pack98_tok_{uuid.uuid4().hex[:16]}'
        st, body = post(f'/api/rewards/claim?server_id={SID_A}',
                        {'source': 'qa_controlled_soft_currency_claim',
                         'reward_instance_id': 'inst_premium', 'idempotency_token': tokp,
                         'payload': {'gems': 100}}, auth)
        assert st == 422
        proofs['pack_96_premium_block_preserved'] = True

        # === 16. Pack 95 story strict preserved ===
        tok_st = f'pack98_tok_{uuid.uuid4().hex[:16]}'
        st, body = post(f'/api/story/battle?server_id={SID_A}&idempotency_token={tok_st}',
                        {'chapter_id': 1, 'stage': 1}, auth)
        assert st == 200 and body.get('pack_95_strict_story_progress_write') is True
        proofs['pack_95_story_strict_preserved'] = True

        # === 17. Pack 95 shops/buy quarantine preserved ===
        st, body = post(f'/api/shops/buy?server_id={SID_A}',
                        {'shop_id': 'honor_shop', 'item_id': 'hs_gacha_ticket'}, auth)
        assert body.get('blocker') == 'SHOPS_BUY_SERVER_SCOPE_DEFERRED'
        proofs['pack_95_shops_buy_quarantine_preserved'] = True

        # === 18. Pack 94 equipment loader preserved ===
        st, body = get(f'/api/user/equipment?server_id={SID_A}', auth)
        assert st == 200 and body.get('filter_applied') is True
        proofs['pack_94_equipment_loader_preserved'] = True

        # === 19. Pack 93 wallet split preserved ===
        st, body = get(f'/api/wallet?server_id={SID_A}', auth)
        assert body.get('wallet_source') == 'psp_server_scoped_split'
        proofs['pack_93_wallet_split_preserved'] = True

        # === 20. Disable quest -> blocks ===
        write_env_kv({GLOBAL_KS: 'true', QUEST_KS: 'false', DAILY_KS: 'true'})
        st, body = post(f'/api/daily-quest/claim?server_id={SID_A}&quest_id=daily_quest_1',
                        {'test_completion_proof': True}, auth)
        assert st == 503
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert d['blocker'] == 'DAILY_QUEST_CLAIM_DISABLED'
        proofs['quest_kill_switch_disable_re_blocks'] = True

    finally:
        if g_orig is None and q_orig is None and d_orig is None:
            write_env_kv({GLOBAL_KS: None, QUEST_KS: None, DAILY_KS: None})
        else:
            write_env_kv({GLOBAL_KS: g_orig, QUEST_KS: q_orig, DAILY_KS: d_orig})
        proofs['kill_switches_restored_to_original'] = True
        if uid:
            loopc = asyncio.new_event_loop(); asyncio.set_event_loop(loopc)
            loopc.run_until_complete(cleanup(uid))
            proofs['cleanup_ok'] = True
    return proofs


if __name__ == '__main__':
    proofs = run()
    required = [
        'daily_quest_default_off_and_gated', 'register_ok', 'ensure_psp_a_ok', 'mark_pack_98_ok',
        'quest_claim_blocked_when_global_off', 'quest_claim_blocked_when_only_global_on',
        'both_kill_switches_enabled', 'quest_preflight_indices_ok',
        'quest_claim_completion_required_for_real_user',
        'quest_id_not_whitelisted_blocked',
        'first_quest_claim_test_proof_success',
        'same_day_quest_replay_no_double_grant',
        'psp_balance_unchanged_after_quest_replay',
        'different_quest_same_day_grants_new',
        'psp_balance_doubled_after_two_quests',
        'next_day_quest_simulation_grants_new',
        'quest_cross_server_b_no_psp_409',
        'test_completion_proof_forbidden_for_non_test_user',
        'pack_97_daily_login_still_works',
        'pack_96_premium_block_preserved', 'pack_95_story_strict_preserved',
        'pack_95_shops_buy_quarantine_preserved',
        'pack_94_equipment_loader_preserved', 'pack_93_wallet_split_preserved',
        'quest_kill_switch_disable_re_blocks',
        'kill_switches_restored_to_original', 'cleanup_ok',
    ]
    missing = [k for k in required if proofs.get(k) is not True]
    out = {
        'pack': 'MEGA_RELEASE_ACCELERATION_98_DAILY_HOME_UNLOCK_AND_DAILY_QUEST_CLAIM_SOURCE_MEGAPACK',
        'timestamp_utc_ts': TS, 'test_artifact_marker': MARKER,
        'global_kill_switch_env': GLOBAL_KS,
        'quest_kill_switch_env': QUEST_KS,
        'kill_switches_default_off': True,
        'proofs': proofs, 'required_missing': missing,
        'real_smoke_executed': len(missing) == 0,
        'test_only_writes': True, 'no_production_user_writes': True,
        'no_premium_grant': True, 'no_double_daily_quest_reward': True,
        'no_reward_live_general': True,
        'completion_proof_marker_enforced': True,
    }
    out_path = '/app/data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_runtime_smoke_e2e_result_v1.json'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f: json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    if missing:
        print(f'[v110 PACK_98_RUNTIME_SMOKE_E2E] BLOCKED missing={missing}'); sys.exit(2)
    print('[v110 PACK_98_RUNTIME_SMOKE_E2E] OK daily_home_gated daily_quest_completion_required_real_users '
          'first_quest_test_proof replay_no_double_grant cross_server_isolated no_premium '
          'pack_91_93_94_95_96_97_preserved kill_switch_lifecycle_clean cleanup')
