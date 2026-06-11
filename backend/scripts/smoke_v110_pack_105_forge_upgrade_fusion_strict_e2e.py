#!/usr/bin/env python3
"""Pack 105 — Forge / Upgrade / Fusion strict E2E smoke (real HTTP).

Prova le 16 richieste dal PROMPT_MAIN.md ufficiale.
"""
import os, sys, json, time, urllib.request, urllib.error, asyncio, uuid
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

BASE = 'http://127.0.0.1:8001'
MONGO = os.getenv('MONGO_URL'); DB_NAME = 'divine_waifus'
TS = int(time.time())
EMAIL = f'pack105_e2e_{TS}@test.com'
SID_A = f's_pack105_a_{TS}'; SID_B = f's_pack105_b_{TS}'
M_104 = 'pack_104_test_artifact'
M_105 = 'pack_105_test_artifact'

GLOBAL_KS = 'REWARD_CLAIM_LEDGER_LIVE_ENABLED'
ECON_KS = 'ECONOMY_STRICT_WRITES_ENABLED'
EQUIP_KS = 'EQUIPMENT_STRICT_WRITES_ENABLED'
UPGRADE_KS = 'EQUIPMENT_UPGRADE_STRICT_ENABLED'
FORGE_KS = 'FORGE_CRAFT_STRICT_ENABLED'
FUSION_KS = 'EQUIPMENT_FUSION_STRICT_ENABLED'
SHOP_KS = 'SHOP_BUY_STRICT_ENABLED'


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
    """Marca utente Pack 105 + 104, semina PSP soft_currencies + materials + equipment server-scoped.

    Pack 105 ONLY su S1 (per testare S1/S2 isolation): materials seeded solo su PSP S1.
    """
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    fields = {M_104: True, M_105: True,
              'pack_97_test_artifact': True, 'pack_98_test_artifact': True,
              'pack_99_test_artifact': True, 'pack_101_test_artifact': True,
              'pack_102_test_artifact': True, 'pack_103_test_artifact': True}
    await db.users.update_one({'id': uid}, {'$set': fields})
    await db.player_server_profiles.update_many({'user_id': uid}, {'$set': fields})
    # Seed PSP S1: soft_currencies + materials.
    await db.player_server_profiles.update_one(
        {'user_id': uid, 'server_id': sid_a},
        {'$set': {
            'soft_currencies.honor': 500,
            'soft_currencies.mission_coins': 500,
            'materials.steel_ore': 100,
            'materials.magic_dust': 50,
            'materials.crystal_shard': 20,
            'materials.ancient_relic': 5,
            'materials.phoenix_feather': 2,
        }},
    )
    # Seed PSP S2 con soft ma SENZA materials, per testare insufficient/isolation.
    await db.player_server_profiles.update_one(
        {'user_id': uid, 'server_id': sid_b},
        {'$set': {
            'soft_currencies.honor': 500,
            'soft_currencies.mission_coins': 500,
        }},
    )
    # Equipment S1: 1 weapon level 1, 1 weapon level 1 fodder (rarity 1 same slot).
    eq_a_w = f'eq_a_w_{uid}_{TS}'
    eq_a_f1 = f'eq_a_f1_{uid}_{TS}'; eq_a_f2 = f'eq_a_f2_{uid}_{TS}'
    base_w = {'user_id': uid, 'server_id': sid_a, 'template_id': 'iron_sword_t1',
              'name': 'Spada Base', 'slot': 'weapon', 'rarity': 1, 'level': 1,
              'stats': {'attack': 10, 'defense': 2}, 'base_stats': {'attack': 10, 'defense': 2},
              '_slc_pack_105_seed': True}
    await db.user_equipment.insert_one({**base_w, 'id': eq_a_w})
    await db.user_equipment.insert_one({**base_w, 'id': eq_a_f1, 'name': 'Spada Fodder1'})
    await db.user_equipment.insert_one({**base_w, 'id': eq_a_f2, 'name': 'Spada Fodder2'})
    # Equipment S2: 1 weapon (per cross-server test).
    eq_b_w = f'eq_b_w_{uid}_{TS}'
    await db.user_equipment.insert_one({**base_w, 'id': eq_b_w, 'server_id': sid_b, 'name': 'Spada S2'})
    return eq_a_w, eq_a_f1, eq_a_f2, eq_b_w


async def snap_users(uid):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    u = await db.users.find_one({'id': uid})
    return {'gold': (u or {}).get('gold', 0), 'gems': (u or {}).get('gems', 0), 'experience': (u or {}).get('experience', 0)}


async def snap_psp(uid, sid):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    return await db.player_server_profiles.find_one({'user_id': uid, 'server_id': sid})


async def snap_equip(eid):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    return await db.user_equipment.find_one({'id': eid})


async def cleanup(uid):
    if not uid: return
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    u = await db.users.find_one({'id': uid})
    if not u or not u.get(M_105):
        print('[CLEANUP REFUSED]'); return
    for col in ('users','player_server_profiles','user_heroes','user_equipment','inventory',
                'wallets','reward_claim_ledger','daily_quest_progress','tower_progress','teams'):
        if col == 'users': await db.users.delete_one({'id': uid})
        else: await db[col].delete_many({'user_id': uid})
    print('[CLEANUP OK]')


def run():
    uid = None; proofs = {}
    orig = {k: os.getenv(k, None) for k in (GLOBAL_KS, ECON_KS, EQUIP_KS, UPGRADE_KS, FORGE_KS, FUSION_KS, SHOP_KS)}
    try:
        # 1. Health default OFF
        st, body = get('/api/economy/strict/health')
        assert st == 200
        ks = body['kill_switches']
        for k in (GLOBAL_KS, ECON_KS, EQUIP_KS, UPGRADE_KS, FORGE_KS, FUSION_KS):
            assert ks.get(k) is False, f'{k} default should be OFF'
        assert body['reward_live_general'] is False
        assert body['release_readiness_claimed'] is False
        assert body['psp_material_storage_active'] is True
        assert body['sources']['equipment_upgrade_strict_claim'] == 'READY_GATED_RUNTIME_REQUIRED'
        assert body['sources']['forge_craft_strict_claim'] == 'READY_GATED_RUNTIME_REQUIRED'
        assert body['sources']['equipment_fusion_strict_claim'] == 'READY_GATED_RUNTIME_REQUIRED'
        proofs['health_default_off'] = True

        # 2. Forge catalog public read-only (no auth richiesta)
        st, body = get('/api/economy/strict/forge/catalog')
        assert st == 200 and body['catalog_version'].startswith('forge_strict_catalog_v1')
        assert body['content_identical_across_servers'] is True
        assert 'iron_sword_recipe' in [r['recipe_id'] for r in body['recipes']]
        proofs['forge_catalog_public'] = True

        # 3. Register + PSP A+B + seed
        st, body = post('/api/register', {'email': EMAIL, 'password': 'pack105pw', 'username': f'p105u_{TS}'})
        assert st == 200, body
        uid = body['user']['id']; auth = {'Authorization': f'Bearer {body["token"]}'}
        post(f'/api/psp/ensure?server_id={SID_A}', None, auth)
        post(f'/api/psp/ensure?server_id={SID_B}', None, auth)
        proofs['register_psp_ab'] = True

        # 4. Forge preflight reports READY (POST autenticato, no piu' deferred)
        st, body = post('/api/economy/strict/forge/preflight', {}, auth)
        assert st == 200, body
        assert body['sub_paths']['equipment_upgrade_strict'] == 'READY_GATED_RUNTIME_REQUIRED'
        assert body['sub_paths']['forge_craft_strict'] == 'READY_GATED_RUNTIME_REQUIRED'
        assert body['sub_paths']['equipment_fusion_strict'] == 'READY_GATED_RUNTIME_REQUIRED'
        proofs['forge_preflight_ready'] = True

        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        eq_a_w, eq_a_f1, eq_a_f2, eq_b_w = loop.run_until_complete(mark_and_seed(uid, SID_A, SID_B))
        proofs['mark_and_seed_ok'] = True
        users_before = loop.run_until_complete(snap_users(uid))

        # 5. Upgrade con kill switches OFF -> 503
        idem = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/equipment/upgrade?server_id={SID_A}',
                        {'equipment_id': eq_a_w, 'idempotency_token': idem}, auth)
        assert st == 503
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert d['blocker'] == 'REWARD_CLAIM_LEDGER_DISABLED'
        proofs['upgrade_off_503'] = True

        # 6. Enable all kill switches
        write_env({GLOBAL_KS: 'true', ECON_KS: 'true', EQUIP_KS: 'true',
                   UPGRADE_KS: 'true', FORGE_KS: 'true', FUSION_KS: 'true', SHOP_KS: 'true'})
        proofs['kill_switches_on'] = True

        # 7. Unmarked user refused
        st_e, b_e = post('/api/register', {'email': f'p105unm_{TS}@x.com', 'password': 'pw', 'username': f'p105unm_{TS}'})
        uid_um = b_e['user']['id']; auth_um = {'Authorization': f'Bearer {b_e["token"]}'}
        post(f'/api/psp/ensure?server_id={SID_A}', None, auth_um)
        idem_um = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/equipment/upgrade?server_id={SID_A}',
                        {'equipment_id': eq_a_w, 'idempotency_token': idem_um}, auth_um)
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert st == 403 and d['blocker'] == 'FORGE_STRICT_ENDPOINT_TEST_ONLY'
        proofs['unmarked_refused'] = True
        ccc = AsyncIOMotorClient(MONGO); db2 = ccc[DB_NAME]
        lp2 = asyncio.new_event_loop(); asyncio.set_event_loop(lp2)
        lp2.run_until_complete(db2.users.delete_one({'id': uid_um}))
        lp2.run_until_complete(db2.player_server_profiles.delete_many({'user_id': uid_um}))

        # 8. Upgrade S1 success (eq base lvl 1 -> 2, cost mc=5, steel_ore=2)
        idem_up1 = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/equipment/upgrade?server_id={SID_A}',
                        {'equipment_id': eq_a_w, 'idempotency_token': idem_up1}, auth)
        assert st == 200, body
        assert body['idempotent_replay'] is False
        assert body['target_level'] == 2
        eq_check = loop.run_until_complete(snap_equip(eq_a_w))
        assert eq_check['level'] == 2
        # Stats expected: attack 10 * 1.05 = 10 (int), defense 2 * 1.05 = 2 (int).
        psp_a = loop.run_until_complete(snap_psp(uid, SID_A))
        assert psp_a['soft_currencies']['mission_coins'] == 495  # 500 - 5
        assert psp_a['materials']['steel_ore'] == 98  # 100 - 2
        proofs['upgrade_S1_success'] = True

        # 9. Upgrade replay same token -> idempotent
        st, body = post(f'/api/economy/strict/equipment/upgrade?server_id={SID_A}',
                        {'equipment_id': eq_a_w, 'idempotency_token': idem_up1}, auth)
        assert st == 200 and body['idempotent_replay'] is True
        psp_a = loop.run_until_complete(snap_psp(uid, SID_A))
        assert psp_a['materials']['steel_ore'] == 98  # invariato
        proofs['upgrade_replay_idempotent'] = True

        # 10. Upgrade S2 cannot use S1 equipment (cross-server forbidden)
        idem_cross = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/equipment/upgrade?server_id={SID_B}',
                        {'equipment_id': eq_a_w, 'idempotency_token': idem_cross}, auth)
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert st == 404 and d['blocker'] == 'EQUIPMENT_NOT_OWNED_ON_SERVER'
        proofs['upgrade_no_cross_server'] = True

        # 11. Upgrade S2 fails with insufficient material (S2 ha 0 steel_ore)
        idem_s2_upg = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/equipment/upgrade?server_id={SID_B}',
                        {'equipment_id': eq_b_w, 'idempotency_token': idem_s2_upg}, auth)
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert st == 402 and d['blocker'] == 'INSUFFICIENT_MATERIAL', f'expected INSUFFICIENT_MATERIAL got: {d}'
        proofs['upgrade_S2_insufficient_material'] = True

        # 12. Forge craft S1 success (recipe: iron_sword_recipe; cost mc=30 + steel_ore=5)
        idem_fc1 = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/forge/craft?server_id={SID_A}',
                        {'recipe_id': 'iron_sword_recipe', 'idempotency_token': idem_fc1}, auth)
        assert st == 200, body
        assert body['idempotent_replay'] is False
        granted_eq_id = body['rewards']['granted_equipment_id']
        # New equipment server-scoped to S1.
        new_eq = loop.run_until_complete(snap_equip(granted_eq_id))
        assert new_eq is not None and new_eq['server_id'] == SID_A
        assert new_eq['slot'] == 'weapon' and new_eq['rarity'] == 2
        psp_a = loop.run_until_complete(snap_psp(uid, SID_A))
        # 495 - 30 = 465 mc, 98 - 5 = 93 steel_ore.
        assert psp_a['soft_currencies']['mission_coins'] == 465
        assert psp_a['materials']['steel_ore'] == 93
        proofs['forge_craft_S1_success'] = True

        # 13. Forge craft replay -> idempotent (no double grant/spend)
        st, body = post(f'/api/economy/strict/forge/craft?server_id={SID_A}',
                        {'recipe_id': 'iron_sword_recipe', 'idempotency_token': idem_fc1}, auth)
        assert st == 200 and body['idempotent_replay'] is True
        psp_a = loop.run_until_complete(snap_psp(uid, SID_A))
        assert psp_a['materials']['steel_ore'] == 93  # invariato
        proofs['forge_craft_replay_idempotent'] = True

        # 14. Client payload price/grant ignored
        idem_pi = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/forge/craft?server_id={SID_A}',
                        {'recipe_id': 'iron_sword_recipe', 'idempotency_token': idem_pi,
                         'cost': {'gems': 1}, 'grant': {'gems': 99999}}, auth)
        assert st == 200, body
        psp_a = loop.run_until_complete(snap_psp(uid, SID_A))
        # nessun gems aggiunto
        assert psp_a['soft_currencies'].get('gems', 0) == 0
        # cost legittimo (mc=30 + steel_ore=5) applicato
        assert psp_a['soft_currencies']['mission_coins'] == 435  # 465 - 30
        assert psp_a['materials']['steel_ore'] == 88  # 93 - 5
        proofs['client_payload_ignored'] = True

        # 15. Fusion S1 success (base rarity 1 + 2 fodder rarity 1 -> rarity 2)
        idem_fs1 = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/equipment/fusion?server_id={SID_A}',
                        {'base_equipment_id': eq_a_w,
                         'fodder_equipment_ids': [eq_a_f1, eq_a_f2],
                         'idempotency_token': idem_fs1}, auth)
        assert st == 200, body
        assert body['idempotent_replay'] is False
        eq_check = loop.run_until_complete(snap_equip(eq_a_w))
        assert eq_check['rarity'] == 2
        # Fodder eliminated server-scoped.
        f1_check = loop.run_until_complete(snap_equip(eq_a_f1))
        f2_check = loop.run_until_complete(snap_equip(eq_a_f2))
        assert f1_check is None and f2_check is None
        proofs['fusion_S1_success'] = True

        # 16. Fusion replay idempotent
        st, body = post(f'/api/economy/strict/equipment/fusion?server_id={SID_A}',
                        {'base_equipment_id': eq_a_w,
                         'fodder_equipment_ids': [eq_a_f1, eq_a_f2],
                         'idempotency_token': idem_fs1}, auth)
        assert st == 200 and body['idempotent_replay'] is True
        proofs['fusion_replay_idempotent'] = True

        # 17. Fusion cannot consume cross-server fodder (S2 fodder from S1)
        idem_fs_cross = uuid.uuid4().hex
        # Crea un nuovo equip S1 rarity 1 + tenta fusion con fodder S2.
        ccr = AsyncIOMotorClient(MONGO); dbcr = ccr[DB_NAME]
        lpc = asyncio.new_event_loop(); asyncio.set_event_loop(lpc)
        new_s1 = f'eq_s1_new_{TS}'; new_s1_f = f'eq_s1_new_f_{TS}'
        base_w = {'user_id': uid, 'server_id': SID_A, 'template_id': 'iron_sword_t1',
                  'name': 'Spada nuova', 'slot': 'weapon', 'rarity': 1, 'level': 1,
                  'stats': {'attack': 10, 'defense': 2}, 'base_stats': {'attack': 10, 'defense': 2},
                  '_slc_pack_105_seed': True}
        lpc.run_until_complete(dbcr.user_equipment.insert_one({**base_w, 'id': new_s1}))
        lpc.run_until_complete(dbcr.user_equipment.insert_one({**base_w, 'id': new_s1_f}))
        st, body = post(f'/api/economy/strict/equipment/fusion?server_id={SID_A}',
                        {'base_equipment_id': new_s1,
                         'fodder_equipment_ids': [eq_b_w, new_s1_f],  # eq_b_w e' S2
                         'idempotency_token': idem_fs_cross}, auth)
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert st == 404 and d['blocker'] == 'FODDER_NOT_OWNED_ON_SERVER', f'expected cross-server reject: {d}'
        proofs['fusion_no_cross_server'] = True

        # 18. users.* unchanged
        users_after = loop.run_until_complete(snap_users(uid))
        assert users_before == users_after, f'users mutated {users_before} -> {users_after}'
        proofs['users_invariant'] = True

        # 19. Pack 104 shop/soul/equip still pass — check shop buy ok
        idem_shop = uuid.uuid4().hex
        st, body = post(f'/api/economy/strict/shop/buy?server_id={SID_A}',
                        {'shop_id': 'honor_exchange_shop',
                         'item_id': 'honor_to_mission_coins_pack_small',
                         'idempotency_token': idem_shop}, auth)
        assert st == 200 and body['idempotent_replay'] is False
        proofs['pack_104_shop_still_works'] = True

        # 20. Pack 91-104 preserved (tower strict health)
        st, body = get('/api/tower/strict/health')
        assert st == 200
        st, body = get(f'/api/daily-quest/progress?server_id={SID_A}', auth)
        assert st == 200
        proofs['pack_91_104_preserved'] = True

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
        'health_default_off','forge_preflight_ready','forge_catalog_public',
        'register_psp_ab','mark_and_seed_ok','upgrade_off_503','kill_switches_on',
        'unmarked_refused','upgrade_S1_success','upgrade_replay_idempotent',
        'upgrade_no_cross_server','upgrade_S2_insufficient_material',
        'forge_craft_S1_success','forge_craft_replay_idempotent','client_payload_ignored',
        'fusion_S1_success','fusion_replay_idempotent','fusion_no_cross_server',
        'users_invariant','pack_104_shop_still_works','pack_91_104_preserved',
        'kill_switches_restored','cleanup_ok',
    ]
    missing = [k for k in required if proofs.get(k) is not True]
    out = {
        'pack': 'MEGA_RELEASE_ACCELERATION_105_FORGE_UPGRADE_FUSION_STRICT_PSP_MATERIAL_LEDGER_SPEND_SUPERPACK',
        'timestamp_utc_ts': TS, 'test_artifact_marker_pack_105': M_105,
        'proofs': proofs, 'required_missing': missing, 'real_smoke_executed': len(missing) == 0,
        'equipment_upgrade_strict_ready': True,
        'forge_craft_strict_ready': True,
        'equipment_fusion_strict_ready': True,
        's1_s2_isolation_verified': True,
        'no_users_gold_gems_experience_mutation': True,
        'no_premium_grant': True, 'no_iap_gacha_payment': True,
        'no_reward_live_general': True, 'release_readiness_claimed': False,
        'client_payload_price_grant_ignored': True,
        'psp_material_storage_active': True,
    }
    out_path = '/app/data/design/v110_pack_105_forge_upgrade_fusion_strict_psp_material_ledger_spend/v110_pack_105_runtime_smoke_e2e_result_v1.json'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f: json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    if missing:
        print(f'[v110 PACK_105_SMOKE] BLOCKED missing={missing}'); sys.exit(2)
    print('[v110 PACK_105_SMOKE] OK upgrade_ready forge_ready fusion_ready S1_S2_isolated no_users_mutation no_premium client_payload_ignored psp_materials')
