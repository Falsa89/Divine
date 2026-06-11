#!/usr/bin/env python3
"""Pack 104 — Shop / Soul Forge / Equipment / Forge strict writes E2E smoke."""
import os, sys, json, time, urllib.request, urllib.error, asyncio, uuid
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

BASE = 'http://127.0.0.1:8001'
MONGO = os.getenv('MONGO_URL'); DB_NAME = 'divine_waifus'
TS = int(time.time())
EMAIL = f'pack104_e2e_{TS}@test.com'
SID_A = f's_pack104_a_{TS}'; SID_B = f's_pack104_b_{TS}'
M_104 = 'pack_104_test_artifact'
M_103 = 'pack_103_test_artifact'
M_102 = 'pack_102_test_artifact'; M_101 = 'pack_101_test_artifact'
M_99 = 'pack_99_test_artifact'; M_98 = 'pack_98_test_artifact'
M_97 = 'pack_97_test_artifact'

GLOBAL_KS = 'REWARD_CLAIM_LEDGER_LIVE_ENABLED'
ECON_KS = 'ECONOMY_STRICT_WRITES_ENABLED'
SHOP_KS = 'SHOP_BUY_STRICT_ENABLED'
SOUL_KS = 'SOUL_FORGE_RETIRE_STRICT_ENABLED'
EQUIP_KS = 'EQUIPMENT_STRICT_WRITES_ENABLED'
FORGE_KS = 'FORGE_STRICT_WRITES_ENABLED'


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


async def mark_and_seed(uid, sid_a, sid_b):
    """Marca utente Pack 104, semina soft_currencies su PSP A+B,
    crea user_heroes e user_equipment server-scoped per S1 e S2."""
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    # Mark tutti i pack
    fields = {M_97: True, M_98: True, M_99: True, M_101: True, M_102: True, M_103: True, M_104: True}
    await db.users.update_one({'id': uid}, {'$set': fields})
    await db.player_server_profiles.update_many({'user_id': uid}, {'$set': fields})
    # Seed PSP soft_currencies su A+B (per pagare shop buy).
    await db.player_server_profiles.update_one(
        {'user_id': uid, 'server_id': sid_a},
        {'$set': {'soft_currencies.honor': 200, 'soft_currencies.mission_coins': 200}},
    )
    await db.player_server_profiles.update_one(
        {'user_id': uid, 'server_id': sid_b},
        {'$set': {'soft_currencies.honor': 200, 'soft_currencies.mission_coins': 200}},
    )
    # User hero server-scoped: 1 su A (per retire test), 1 su B (per cross-server check), 1 su A (per equip).
    h_a = f'uh_{uid}_a_{TS}'; h_b = f'uh_{uid}_b_{TS}'; h_a2 = f'uh_{uid}_a2_{TS}'
    base_h = {'user_id': uid, 'hero_id': 'shadow_walker_001', 'stars': 3, 'level': 10, '_slc_pack_104_seed': True}
    await db.user_heroes.insert_one({**base_h, 'id': h_a, 'server_id': sid_a})
    await db.user_heroes.insert_one({**base_h, 'id': h_b, 'server_id': sid_b})
    await db.user_heroes.insert_one({**base_h, 'id': h_a2, 'server_id': sid_a})
    # Equipment server-scoped (S1): 1 weapon + 1 armor.
    eq_w_a = f'eq_w_{uid}_a_{TS}'; eq_a_a = f'eq_a_{uid}_a_{TS}'
    base_e = {'user_id': uid, 'template_id': 'iron_sword_t1', '_slc_pack_104_seed': True}
    await db.user_equipment.insert_one({**base_e, 'id': eq_w_a, 'server_id': sid_a, 'slot': 'weapon'})
    await db.user_equipment.insert_one({**base_e, 'id': eq_a_a, 'server_id': sid_a, 'slot': 'armor'})
    # Equipment S2 (per check no cross-server)
    eq_w_b = f'eq_w_{uid}_b_{TS}'
    await db.user_equipment.insert_one({**base_e, 'id': eq_w_b, 'server_id': sid_b, 'slot': 'weapon'})
    return h_a, h_b, h_a2, eq_w_a, eq_a_a, eq_w_b


async def snap_users(uid):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    u = await db.users.find_one({'id': uid})
    return {'gold': (u or {}).get('gold', 0), 'gems': (u or {}).get('gems', 0), 'experience': (u or {}).get('experience', 0)}


async def snap_psp(uid, sid):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    return await db.player_server_profiles.find_one({'user_id': uid, 'server_id': sid})


async def snap_hero(hid):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    return await db.user_heroes.find_one({'id': hid})


async def snap_equip(eid):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    return await db.user_equipment.find_one({'id': eid})


async def cleanup(uid):
    if not uid: return
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    u = await db.users.find_one({'id': uid})
    if not u or not u.get(M_104):
        print('[CLEANUP REFUSED]'); return
    for col in ('users','player_server_profiles','user_heroes','user_equipment','inventory',
                'wallets','reward_claim_ledger','daily_quest_progress','tower_progress',
                'teams'):
        if col == 'users': await db.users.delete_one({'id': uid})
        else: await db[col].delete_many({'user_id': uid})
    print('[CLEANUP OK]')


def run():
    uid = None; proofs = {}
    orig = {k: os.getenv(k, None) for k in (GLOBAL_KS, ECON_KS, SHOP_KS, SOUL_KS, EQUIP_KS, FORGE_KS)}
    try:
        # 1. Health default OFF
        st, body = get('/api/economy/strict/health')
        assert st == 200
        ks = body['kill_switches']
        for k in (GLOBAL_KS, ECON_KS, SHOP_KS, SOUL_KS, EQUIP_KS, FORGE_KS):
            assert ks.get(k) is False, f'{k} default should be OFF'
        assert body['reward_live_general'] is False
        assert body['premium_grants'] is False
        assert body['release_readiness_claimed'] is False
        assert body['no_iap_gacha_payment'] is True
        assert body['sources']['forge_upgrade_strict'] == 'FORGE_UPGRADE_STRICT_DEFERRED'
        assert body['sources']['equipment_fusion_strict'] == 'EQUIPMENT_FUSION_STRICT_DEFERRED'
        proofs['health_default_off'] = True

        # 2. Register + PSP A+B + seed
        st, body = post('/api/register', {'email': EMAIL, 'password': 'pack104pw', 'username': f'p104u_{TS}'})
        assert st == 200, body
        uid = body['user']['id']; auth = {'Authorization': f'Bearer {body["token"]}'}
        post(f'/api/psp/ensure?server_id={SID_A}', None, auth)
        post(f'/api/psp/ensure?server_id={SID_B}', None, auth)
        proofs['register_psp_ab'] = True

        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        h_a, h_b, h_a2, eq_w_a, eq_a_a, eq_w_b = loop.run_until_complete(mark_and_seed(uid, SID_A, SID_B))
        proofs['mark_and_seed_ok'] = True
        users_before = loop.run_until_complete(snap_users(uid))

        # 3. Shop buy con kill switches OFF -> 503
        idem = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/shop/buy?server_id={SID_A}',
                        {'shop_id': 'honor_exchange_shop',
                         'item_id': 'honor_to_mission_coins_pack_small',
                         'idempotency_token': idem}, auth)
        assert st == 503
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert d['blocker'] == 'REWARD_CLAIM_LEDGER_DISABLED'
        proofs['shop_buy_off_503'] = True

        # 4. Abilita tutti i kill switch
        write_env({GLOBAL_KS: 'true', ECON_KS: 'true', SHOP_KS: 'true', SOUL_KS: 'true', EQUIP_KS: 'true', FORGE_KS: 'true'})
        proofs['kill_switches_on'] = True

        # 5. Unmarked user refused
        st_e, b_e = post('/api/register', {'email': f'p104unm_{TS}@x.com', 'password': 'pw', 'username': f'p104unm_{TS}'})
        uid_um = b_e['user']['id']; auth_um = {'Authorization': f'Bearer {b_e["token"]}'}
        post(f'/api/psp/ensure?server_id={SID_A}', None, auth_um)
        idem_um = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/shop/buy?server_id={SID_A}',
                        {'shop_id': 'honor_exchange_shop',
                         'item_id': 'honor_to_mission_coins_pack_small',
                         'idempotency_token': idem_um}, auth_um)
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert st == 403 and d['blocker'] == 'ECONOMY_STRICT_ENDPOINT_TEST_ONLY'
        proofs['unmarked_refused'] = True
        # cleanup unmarked
        ccc = AsyncIOMotorClient(MONGO); db2 = ccc[DB_NAME]
        lp2 = asyncio.new_event_loop(); asyncio.set_event_loop(lp2)
        lp2.run_until_complete(db2.users.delete_one({'id': uid_um}))
        lp2.run_until_complete(db2.player_server_profiles.delete_many({'user_id': uid_um}))

        # 6. Shop buy A success (honor: -20, +30 mission_coins)
        idem_s1 = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/shop/buy?server_id={SID_A}',
                        {'shop_id': 'honor_exchange_shop',
                         'item_id': 'honor_to_mission_coins_pack_small',
                         'idempotency_token': idem_s1}, auth)
        assert st == 200, body
        assert body['idempotent_replay'] is False
        assert body['claim_source'] == 'shop_buy_strict_claim'
        psp_a = loop.run_until_complete(snap_psp(uid, SID_A))
        soft_a = psp_a.get('soft_currencies') or {}
        # 200-20 honor = 180, 200+30 mc = 230
        assert soft_a.get('honor') == 180, f'unexpected honor: {soft_a}'
        assert soft_a.get('mission_coins') == 230, f'unexpected mc: {soft_a}'
        proofs['shop_buy_S1_success'] = True

        # 7. Shop buy replay same token -> idempotent
        st, body = post(f'/api/economy/strict/shop/buy?server_id={SID_A}',
                        {'shop_id': 'honor_exchange_shop',
                         'item_id': 'honor_to_mission_coins_pack_small',
                         'idempotency_token': idem_s1}, auth)
        assert st == 200 and body['idempotent_replay'] is True
        psp_a = loop.run_until_complete(snap_psp(uid, SID_A))
        soft_a = psp_a.get('soft_currencies') or {}
        assert soft_a.get('honor') == 180 and soft_a.get('mission_coins') == 230
        proofs['shop_buy_replay_idempotent'] = True

        # 8. Shop buy S2 unaffected
        psp_b = loop.run_until_complete(snap_psp(uid, SID_B))
        soft_b = psp_b.get('soft_currencies') or {}
        assert soft_b.get('honor') == 200 and soft_b.get('mission_coins') == 200
        proofs['shop_buy_S2_unaffected'] = True

        # 9. Soul forge retire S1 success (3 stars hero -> band 3-4: +10 mc, +5 honor)
        idem_sf1 = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/soul-forge/retire?server_id={SID_A}',
                        {'user_hero_id': h_a, 'idempotency_token': idem_sf1}, auth)
        assert st == 200, body
        assert body['idempotent_replay'] is False
        assert body['claim_source'] == 'soul_forge_retire_strict_claim'
        assert body['stars'] == 3
        psp_a = loop.run_until_complete(snap_psp(uid, SID_A))
        soft_a = psp_a.get('soft_currencies') or {}
        assert soft_a.get('honor') == 185 and soft_a.get('mission_coins') == 240
        # Hero deve essere eliminato
        h_check = loop.run_until_complete(snap_hero(h_a))
        assert h_check is None
        proofs['soul_forge_retire_S1_success'] = True

        # 10. Soul forge retire replay -> idempotent (anche se hero gia` rimosso)
        st, body = post(f'/api/economy/strict/soul-forge/retire?server_id={SID_A}',
                        {'user_hero_id': h_a, 'idempotency_token': idem_sf1}, auth)
        # claim_key e' lo stesso quindi idempotent_replay True OPPURE 404 HERO_NOT_OWNED.
        # Il check idempotency PRE-check viene prima del check ownership, quindi dovrebbe
        # ritornare 200 idempotent.
        assert st == 200 and body['idempotent_replay'] is True
        proofs['soul_forge_replay_idempotent'] = True

        # 11. Soul forge S1 NON puo` retire hero S2 (cross-server forbidden)
        idem_sf_cross = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/soul-forge/retire?server_id={SID_A}',
                        {'user_hero_id': h_b, 'idempotency_token': idem_sf_cross}, auth)
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert st == 404 and d['blocker'] == 'HERO_NOT_OWNED_ON_SERVER'
        # Verifica che hero B sia ancora vivo
        h_b_check = loop.run_until_complete(snap_hero(h_b))
        assert h_b_check is not None and h_b_check['server_id'] == SID_B
        proofs['soul_forge_no_cross_server'] = True

        # 12. Equipment equip S1
        idem_eq1 = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/equipment/equip?server_id={SID_A}',
                        {'equipment_id': eq_w_a, 'user_hero_id': h_a2, 'idempotency_token': idem_eq1}, auth)
        assert st == 200, body
        assert body['idempotent_replay'] is False
        eq_check = loop.run_until_complete(snap_equip(eq_w_a))
        assert eq_check.get('equipped_to') == h_a2
        proofs['equipment_equip_S1_success'] = True

        # 13. Equipment equip replay -> idempotent
        st, body = post(f'/api/economy/strict/equipment/equip?server_id={SID_A}',
                        {'equipment_id': eq_w_a, 'user_hero_id': h_a2, 'idempotency_token': idem_eq1}, auth)
        assert st == 200 and body['idempotent_replay'] is True
        proofs['equipment_equip_replay_idempotent'] = True

        # 14. Equipment S1 NON puo` equip equipment S2 (cross-server)
        idem_eq_cross = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/equipment/equip?server_id={SID_A}',
                        {'equipment_id': eq_w_b, 'user_hero_id': h_a2, 'idempotency_token': idem_eq_cross}, auth)
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert st == 404 and d['blocker'] == 'EQUIPMENT_NOT_OWNED_ON_SERVER'
        proofs['equipment_no_cross_server'] = True

        # 15. Equipment unequip S1
        idem_uq1 = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/equipment/unequip?server_id={SID_A}',
                        {'equipment_id': eq_w_a, 'idempotency_token': idem_uq1}, auth)
        assert st == 200 and body['idempotent_replay'] is False
        eq_check = loop.run_until_complete(snap_equip(eq_w_a))
        assert 'equipped_to' not in eq_check or eq_check.get('equipped_to') in (None, '')
        proofs['equipment_unequip_S1_success'] = True

        # 16. Forge preflight DEFERRED
        st, body = post(f'/api/economy/strict/forge/preflight?server_id={SID_A}', {}, auth)
        assert st == 503
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert d['blocker_forge_upgrade'] == 'FORGE_UPGRADE_STRICT_DEFERRED'
        assert d['blocker_equipment_fusion'] == 'EQUIPMENT_FUSION_STRICT_DEFERRED'
        proofs['forge_deferred_honest'] = True

        # 17. Client payload price ignored (cost/grant da catalog, no client trust)
        # tenta di "spedire" un payload extra (Pydantic lo ignora poi che' modello non lo dichiara)
        idem_p_ignore = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/shop/buy?server_id={SID_A}',
                        {'shop_id': 'honor_exchange_shop',
                         'item_id': 'honor_to_mission_coins_pack_small',
                         'idempotency_token': idem_p_ignore,
                         'cost': {'gems': 1},  # client trying to override price with gems
                         'grant': {'gems': 99999}},  # client trying to override grant with gems
                        auth)
        # Se shop_buy ha avuto successo, il grant deve essere ancora dal catalog ufficiale (+30 mc, -20 honor).
        assert st == 200, body
        psp_a = loop.run_until_complete(snap_psp(uid, SID_A))
        soft_a = psp_a.get('soft_currencies') or {}
        # 185 honor -20 = 165, 240 mc +30 = 270
        assert soft_a.get('honor') == 165 and soft_a.get('mission_coins') == 270
        # NESSUN gems incrementato.
        assert soft_a.get('gems', 0) == 0
        proofs['client_payload_ignored'] = True

        # 18. users.* invariato end-to-end
        users_after = loop.run_until_complete(snap_users(uid))
        assert users_before == users_after, f'users mutated {users_before} -> {users_after}'
        proofs['users_invariant'] = True

        # 19. Packs 91-103 preserved (tower strict, daily quest tracker, daily quest claim)
        st, body = get('/api/tower/strict/health')
        assert st == 200 and body['tower_progress_server_scope_status']
        st, body = get(f'/api/daily-quest/progress?server_id={SID_A}', auth)
        assert st == 200
        proofs['pack_91_103_preserved'] = True

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
    required = [
        'health_default_off', 'register_psp_ab', 'mark_and_seed_ok',
        'shop_buy_off_503', 'kill_switches_on', 'unmarked_refused',
        'shop_buy_S1_success', 'shop_buy_replay_idempotent', 'shop_buy_S2_unaffected',
        'soul_forge_retire_S1_success', 'soul_forge_replay_idempotent', 'soul_forge_no_cross_server',
        'equipment_equip_S1_success', 'equipment_equip_replay_idempotent', 'equipment_no_cross_server',
        'equipment_unequip_S1_success', 'forge_deferred_honest',
        'client_payload_ignored', 'users_invariant', 'pack_91_103_preserved',
        'kill_switches_restored', 'cleanup_ok',
    ]
    missing = [k for k in required if proofs.get(k) is not True]
    out = {
        'pack': 'MEGA_RELEASE_ACCELERATION_104_SHOP_SOUL_EQUIPMENT_FORGE_STRICT_WRITES_SUPERPACK',
        'timestamp_utc_ts': TS, 'test_artifact_marker_pack_104': M_104,
        'proofs': proofs, 'required_missing': missing, 'real_smoke_executed': len(missing) == 0,
        'shop_buy_strict_ready': True, 'soul_forge_retire_strict_ready': True,
        'equipment_strict_writes_ready': True,
        'forge_strict_ready': False,
        'forge_deferred_blocker': 'FORGE_UPGRADE_STRICT_DEFERRED / EQUIPMENT_FUSION_STRICT_DEFERRED',
        's1_s2_isolation_verified': True,
        'no_users_gold_gems_experience_mutation': True,
        'no_premium_grant': True, 'no_iap_gacha_payment': True,
        'no_reward_live_general': True, 'release_readiness_claimed': False,
        'client_payload_price_grant_ignored': True,
    }
    out_path = '/app/data/design/v110_pack_104_shop_soul_equipment_forge_strict_writes/v110_pack_104_runtime_smoke_e2e_result_v1.json'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f: json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    if missing:
        print(f'[v110 PACK_104_SMOKE] BLOCKED missing={missing}'); sys.exit(2)
    print('[v110 PACK_104_SMOKE] OK shop_buy_ready soul_forge_ready equipment_strict_ready forge_deferred_honest S1_S2_isolated no_users_mutation no_premium')
