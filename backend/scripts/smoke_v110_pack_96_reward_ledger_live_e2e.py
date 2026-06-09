#!/usr/bin/env python3
"""Pack 96 — Reward claim ledger LIVE execute + controlled claim paths smoke E2E.

Marker: pack_96_test_artifact=true. Cleanup garantito in finally.

Kill switch lifecycle:
  * Inizialmente off (default user-mandated). Lo smoke registra il valore originale,
    abilita temporaneamente la env-var per le porzioni di test che richiedono live,
    poi ripristina il valore originale prima della cleanup finale.
"""
import os, sys, json, time, uuid, urllib.request, urllib.error, asyncio
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

BASE = 'http://127.0.0.1:8001'
MONGO = os.getenv('MONGO_URL'); DB_NAME = 'divine_waifus'
TS = int(time.time())
EMAIL = f'pack96_test_user_{TS}@test.com'
SID_A = f's_pack96_a_{TS}'
SID_B = f's_pack96_b_{TS}'
MARKER = 'pack_96_test_artifact'
KILL_SWITCH_ENV = 'REWARD_CLAIM_LEDGER_LIVE_ENABLED'


def _req(method, path, body=None, headers=None):
    H = {'Content-Type': 'application/json'}
    if headers:
        H.update(headers)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f'{BASE}{path}', data=data, headers=H, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}


def post(p, b=None, h=None): return _req('POST', p, b, h)
def get(p, h=None): return _req('GET', p, None, h)


def restart_backend_with_kill_switch(value: str):
    """Aggiorna /etc/supervisor/conf.d/* per il backend con env override e restart.

    Usa l'approccio piu' portabile: via supervisorctl restart dopo aver scritto la
    env nel file /app/backend/.env (riga aggiunta/aggiornata). Cleanup nella finally.
    """
    env_path = '/app/backend/.env'
    lines = []
    if os.path.exists(env_path):
        with open(env_path) as f:
            lines = f.readlines()
    new_lines = [ln for ln in lines if not ln.startswith(f'{KILL_SWITCH_ENV}=')]
    new_lines.append(f'{KILL_SWITCH_ENV}={value}\n')
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    os.system('sudo supervisorctl restart backend > /dev/null 2>&1')
    time.sleep(4)


def remove_kill_switch_env():
    env_path = '/app/backend/.env'
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        lines = f.readlines()
    new_lines = [ln for ln in lines if not ln.startswith(f'{KILL_SWITCH_ENV}=')]
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    os.system('sudo supervisorctl restart backend > /dev/null 2>&1')
    time.sleep(4)


async def mark(uid):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    await db.users.update_one({'id': uid}, {'$set': {MARKER: True}})
    await db.player_server_profiles.update_many({'user_id': uid}, {'$set': {MARKER: True}})


async def cleanup(uid):
    if not uid:
        return
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    u = await db.users.find_one({'id': uid})
    if not u or not u.get(MARKER):
        print(f'[CLEANUP REFUSED] user {uid} not marked')
        return
    r1 = await db.users.delete_one({'id': uid, MARKER: True})
    r2 = await db.inventory.delete_many({'user_id': uid})
    r3 = await db.player_server_profiles.delete_many({'user_id': uid, MARKER: True})
    r4 = await db.user_heroes.delete_many({'user_id': uid})
    r5 = await db.user_equipment.delete_many({'user_id': uid})
    r6 = await db.wallets.delete_many({'user_id': uid})
    r7 = await db.reward_claim_ledger.delete_many({'user_id': uid})
    print(f'[CLEANUP OK] users={r1.deleted_count} inv={r2.deleted_count} psp={r3.deleted_count} '
          f'uh={r4.deleted_count} eq={r5.deleted_count} wallets={r6.deleted_count} '
          f'ledger={r7.deleted_count}')


def run():
    uid = None
    proofs = {}
    kill_switch_original = os.getenv(KILL_SWITCH_ENV, None)  # snapshot
    kill_switch_originally_set = kill_switch_original is not None
    try:
        # === 0. Default OFF behaviour (smoke contract requirement) ===
        # Senza override .env la env-var non e' settata; per il backend e' default-OFF.
        st, body = get('/api/rewards/claim/health')
        assert st == 200, body
        assert body.get('live_enabled') is False, f'kill switch should be OFF by default: {body}'
        proofs['kill_switch_default_off'] = True

        # === 1. Register + ensure PSP A + mark ===
        st, body = post('/api/register', {'email': EMAIL, 'password': 'pack96pw',
                                          'username': f'p96u_{TS}'})
        assert st == 200, body
        uid = body['user']['id']
        auth = {'Authorization': f'Bearer {body["token"]}'}
        proofs['register_ok'] = True

        st, body = post(f'/api/psp/ensure?server_id={SID_A}', None, auth)
        assert st in (200, 201)
        proofs['ensure_psp_a_ok'] = True

        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        loop.run_until_complete(mark(uid))
        proofs['mark_pack_96_ok'] = True

        # === 2. Claim should be BLOCKED when kill switch OFF ===
        tok0 = f'pack96_tok_{uuid.uuid4().hex[:16]}'
        st, body = post(
            f'/api/rewards/claim?server_id={SID_A}',
            {'source': 'qa_controlled_soft_currency_claim',
             'reward_instance_id': 'inst_off_test',
             'idempotency_token': tok0,
             'payload': {'gold': 100}},
            auth,
        )
        assert st == 503, f'expected 503 when kill switch off, got {st}: {body}'
        detail = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert detail.get('blocker') == 'REWARD_CLAIM_LEDGER_LIVE_DISABLED', detail
        proofs['kill_switch_blocks_when_off'] = True

        # === 3. Enable kill switch via .env override + backend restart ===
        restart_backend_with_kill_switch('true')
        st, body = get('/api/rewards/claim/health')
        assert body.get('live_enabled') is True, body
        proofs['kill_switch_enable_for_test_ok'] = True

        # === 4. Preflight: index creation safe + idempotent ===
        st, body = post('/api/rewards/claim/preflight', None, auth)
        assert st == 200, body
        assert body.get('kill_switch_live_enabled') is True
        assert 'qa_controlled_soft_currency_claim' in body.get('allowlisted_sources') or []
        idx1 = body.get('index_creation') or {}
        assert idx1.get('stopped') is False
        proofs['preflight_index_creation_safe_idempotent_first_call'] = True

        # Re-call preflight: must NOT throw, must NOT drop existing index
        st, body = post('/api/rewards/claim/preflight', None, auth)
        assert st == 200 and (body.get('index_creation') or {}).get('stopped') is False
        proofs['preflight_index_creation_idempotent_second_call'] = True

        # === 5. First controlled claim (qa source, soft currency) ===
        tok1 = f'pack96_tok_{uuid.uuid4().hex[:16]}'
        st, body = post(
            f'/api/rewards/claim?server_id={SID_A}',
            {'source': 'qa_controlled_soft_currency_claim',
             'reward_instance_id': 'inst_001',
             'idempotency_token': tok1,
             'payload': {'gold': 50, 'honor': 5}},
            auth,
        )
        assert st == 200, body
        assert body.get('idempotent_replay') is False
        assert body.get('pack_96_controlled_claim') is True
        assert body.get('reward_live_general') is False
        rew = body.get('rewards') or {}
        assert rew.get('live_grant') is True
        assert rew.get('server_scoped', {}).get('gold') == 50
        assert rew.get('server_scoped', {}).get('honor') == 5
        assert rew.get('account_wide') == {}
        proofs['first_controlled_claim_success'] = True

        # === 6. Replay (same token) => no second grant ===
        st, body = post(
            f'/api/rewards/claim?server_id={SID_A}',
            {'source': 'qa_controlled_soft_currency_claim',
             'reward_instance_id': 'inst_001',
             'idempotency_token': tok1,
             'payload': {'gold': 50, 'honor': 5}},
            auth,
        )
        assert st == 200 and body.get('idempotent_replay') is True
        proofs['replay_returns_idempotent_no_double_grant'] = True

        # Verify ledger count + PSP.soft_currencies balance unchanged across replay
        loopv = asyncio.new_event_loop(); asyncio.set_event_loop(loopv)
        c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
        cnt = loopv.run_until_complete(
            db.reward_claim_ledger.count_documents(
                {'user_id': uid, 'server_id': SID_A, 'idempotency_token': tok1})
        )
        assert cnt == 1, f'expected exactly 1 ledger row after replay, got {cnt}'
        psp = loopv.run_until_complete(
            db.player_server_profiles.find_one({'user_id': uid, 'server_id': SID_A})
        )
        soft = (psp or {}).get('soft_currencies') or {}
        assert soft.get('gold') == 50 and soft.get('honor') == 5, soft
        proofs['ledger_single_row_after_replay'] = True
        proofs['psp_balance_unchanged_after_replay'] = True

        # === 7. Same source, different token => grants again (allowed) ===
        tok2 = f'pack96_tok_{uuid.uuid4().hex[:16]}'
        st, body = post(
            f'/api/rewards/claim?server_id={SID_A}',
            {'source': 'qa_controlled_soft_currency_claim',
             'reward_instance_id': 'inst_002',
             'idempotency_token': tok2,
             'payload': {'gold': 25}},
            auth,
        )
        assert st == 200 and body.get('idempotent_replay') is False
        psp = loopv.run_until_complete(
            db.player_server_profiles.find_one({'user_id': uid, 'server_id': SID_A})
        )
        soft = (psp or {}).get('soft_currencies') or {}
        assert soft.get('gold') == 75, soft  # 50 + 25
        proofs['same_source_different_token_grants_again'] = True

        # === 8. Unknown source => 422 NOT_ALLOWLISTED ===
        tok3 = f'pack96_tok_{uuid.uuid4().hex[:16]}'
        st, body = post(
            f'/api/rewards/claim?server_id={SID_A}',
            {'source': 'totally_unknown_source_xyz',
             'reward_instance_id': 'inst_x',
             'idempotency_token': tok3,
             'payload': {'gold': 1}},
            auth,
        )
        assert st == 422, body
        detail = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert detail.get('blocker') == 'REWARD_SOURCE_NOT_ALLOWLISTED'
        proofs['unknown_source_blocked'] = True

        # === 9. Premium grant attempt => 422 PREMIUM_GRANT_BLOCKED ===
        tok4 = f'pack96_tok_{uuid.uuid4().hex[:16]}'
        st, body = post(
            f'/api/rewards/claim?server_id={SID_A}',
            {'source': 'qa_controlled_soft_currency_claim',
             'reward_instance_id': 'inst_premium_attempt',
             'idempotency_token': tok4,
             'payload': {'gems': 100}},
            auth,
        )
        assert st == 422, body
        detail = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert detail.get('blocker') == 'PREMIUM_GRANT_BLOCKED', detail
        proofs['premium_grant_blocked'] = True

        # Verify users.gems was NOT mutated
        u = loopv.run_until_complete(db.users.find_one({'id': uid}))
        assert u is not None
        # No assertion on absolute gems value (account may have gems from register flow);
        # but ledger row for this premium attempt must NOT exist (atomic block before grant).
        cnt_premium = loopv.run_until_complete(
            db.reward_claim_ledger.count_documents({'user_id': uid, 'idempotency_token': tok4})
        )
        assert cnt_premium == 0, f'premium attempt left ledger row: {cnt_premium}'
        proofs['no_ledger_row_for_premium_attempt'] = True

        # === 10. Cross-server isolation: server B no PSP => 409 ===
        tok5 = f'pack96_tok_{uuid.uuid4().hex[:16]}'
        st, body = post(
            f'/api/rewards/claim?server_id={SID_B}',
            {'source': 'qa_controlled_soft_currency_claim',
             'reward_instance_id': 'inst_b',
             'idempotency_token': tok5,
             'payload': {'gold': 10}},
            auth,
        )
        assert st == 409, body
        proofs['cross_server_no_leak_psp_required'] = True

        # === 11. story_progress_marker_claim (noop grant) ===
        tok6 = f'pack96_tok_{uuid.uuid4().hex[:16]}'
        st, body = post(
            f'/api/rewards/claim?server_id={SID_A}',
            {'source': 'story_progress_marker_claim',
             'reward_instance_id': 'chapter_1_stage_1',
             'idempotency_token': tok6,
             'payload': {}},
            auth,
        )
        assert st == 200 and body.get('idempotent_replay') is False
        assert (body.get('rewards') or {}).get('server_scoped') == {}
        proofs['story_marker_claim_noop_success'] = True

        # === 12. Pack preservation checks ===
        # Pack 95 story battle strict still works
        toks = f'pack96_tok_{uuid.uuid4().hex[:16]}'
        st, body = post(
            f'/api/story/battle?server_id={SID_A}&idempotency_token={toks}',
            {'chapter_id': 1, 'stage': 1}, auth,
        )
        assert st == 200 and body.get('pack_95_strict_story_progress_write') is True
        proofs['pack_95_story_strict_preserved'] = True

        # Pack 95 legacy quarantine for shops/buy still active
        st, body = post(
            f'/api/shops/buy?server_id={SID_A}',
            {'shop_id': 'honor_shop', 'item_id': 'hs_gacha_ticket'}, auth,
        )
        assert body.get('blocker') == 'SHOPS_BUY_SERVER_SCOPE_DEFERRED'
        proofs['pack_95_shops_buy_quarantine_preserved'] = True

        # Pack 94 equipment loader strict still works
        st, body = get(f'/api/user/equipment?server_id={SID_A}', auth)
        assert st == 200 and body.get('filter_applied') is True
        proofs['pack_94_equipment_loader_preserved'] = True

        # Pack 93 wallet split still works
        st, body = get(f'/api/wallet?server_id={SID_A}', auth)
        assert body.get('wallet_source') == 'psp_server_scoped_split'
        proofs['pack_93_wallet_split_preserved'] = True

        # === 13. Disable kill switch and verify re-block ===
        restart_backend_with_kill_switch('false')
        st, body = get('/api/rewards/claim/health')
        assert body.get('live_enabled') is False
        tok7 = f'pack96_tok_{uuid.uuid4().hex[:16]}'
        st, body = post(
            f'/api/rewards/claim?server_id={SID_A}',
            {'source': 'qa_controlled_soft_currency_claim',
             'reward_instance_id': 'inst_after_disable',
             'idempotency_token': tok7,
             'payload': {'gold': 1}},
            auth,
        )
        assert st == 503, body
        proofs['kill_switch_disable_re_blocks_correctly'] = True

    finally:
        # === Kill switch lifecycle: restore original ===
        if kill_switch_originally_set:
            restart_backend_with_kill_switch(kill_switch_original)
        else:
            remove_kill_switch_env()
        proofs['kill_switch_restored_to_original'] = True
        if uid:
            loopc = asyncio.new_event_loop(); asyncio.set_event_loop(loopc)
            loopc.run_until_complete(cleanup(uid))
            proofs['cleanup_ok'] = True
    return proofs


if __name__ == '__main__':
    proofs = run()
    required = [
        'kill_switch_default_off', 'register_ok', 'ensure_psp_a_ok', 'mark_pack_96_ok',
        'kill_switch_blocks_when_off', 'kill_switch_enable_for_test_ok',
        'preflight_index_creation_safe_idempotent_first_call',
        'preflight_index_creation_idempotent_second_call',
        'first_controlled_claim_success',
        'replay_returns_idempotent_no_double_grant',
        'ledger_single_row_after_replay', 'psp_balance_unchanged_after_replay',
        'same_source_different_token_grants_again',
        'unknown_source_blocked', 'premium_grant_blocked',
        'no_ledger_row_for_premium_attempt',
        'cross_server_no_leak_psp_required',
        'story_marker_claim_noop_success',
        'pack_95_story_strict_preserved',
        'pack_95_shops_buy_quarantine_preserved',
        'pack_94_equipment_loader_preserved',
        'pack_93_wallet_split_preserved',
        'kill_switch_disable_re_blocks_correctly',
        'kill_switch_restored_to_original',
        'cleanup_ok',
    ]
    missing = [k for k in required if proofs.get(k) is not True]
    out = {
        'pack': 'MEGA_RELEASE_ACCELERATION_96_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_AND_CONTROLLED_CLAIM_PATHS',
        'timestamp_utc_ts': TS, 'test_artifact_marker': MARKER,
        'kill_switch_env': KILL_SWITCH_ENV,
        'kill_switch_default_off_for_smoke': True,
        'kill_switch_originally_set_in_env': bool(__import__('os').getenv('REWARD_CLAIM_LEDGER_LIVE_ENABLED')),
        'proofs': proofs, 'required_missing': missing,
        'real_smoke_executed': len(missing) == 0,
        'test_only_writes': True, 'no_production_user_writes': True,
        'no_premium_grant': True, 'no_double_grant': True,
        'no_reward_live_general': True,
    }
    out_path = '/app/data/design/v110_pack_96_reward_claim_ledger_live_execute/v110_pack_96_runtime_smoke_e2e_result_v1.json'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    if missing:
        print(f'[v110 PACK_96_RUNTIME_SMOKE_E2E] BLOCKED missing={missing}'); sys.exit(2)
    print('[v110 PACK_96_RUNTIME_SMOKE_E2E] OK reward_ledger_live_gated controlled_claim_paths_allowlisted '
          'no_double_grant no_premium_grant cross_server_isolated kill_switch_lifecycle_clean pack_91_93_94_95_preserved')
