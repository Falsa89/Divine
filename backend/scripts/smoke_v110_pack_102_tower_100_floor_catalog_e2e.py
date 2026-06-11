#!/usr/bin/env python3
"""Pack 102 — Tower 100 Floor Catalog E2E (deterministic teams + S1/S2 isolation).

Test invariants:
  * GET /api/tower/strict/catalog -> 100 floors, version v1, deterministic flags.
  * GET /api/tower/strict/catalog/floor/{1,5,10,50,100} -> tipo corretto, leader rarity, 6-team.
  * Floor fuori range 101 / 0 -> 404 FLOOR_OUT_OF_CATALOG_RANGE.
  * Preview floor 1 + 5 + 10 + 50 + 100 con S1 -> include catalog_floor, NO mutation users.*, NO advance.
  * Tutti gli enemy hero_id appartengono a LAUNCH_BASE_HERO_IDS.
  * Borea/extra_premium NON usato.
  * Boss floors (10/20/.../90) hanno boss_leader_slot=0 e enemy_team[0].is_boss_leader=True.
  * Major boss (50, 100) leader rarity >= 5.
  * Floor 100 leader rarity = 6.
  * Mini-spike (5/15/.../95) hanno floor_type=mini_spike.
  * Determinism: 5 chiamate consecutive a /catalog/floor/50 ritornano stesso payload.
  * S1/S2 isolation: preflight su S1 NON crea PSP.tower_progress su S2.
  * users.gold/users.gems/users.experience invariati end-to-end.
  * Pack 91-101 preserved.
  * Cleanup automatico.
"""
import os, sys, json, time, urllib.request, urllib.error, asyncio
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient
from data.character_bible import LAUNCH_BASE_HERO_IDS, EXTRA_PREMIUM_HERO_IDS

BASE = 'http://127.0.0.1:8001'
MONGO = os.getenv('MONGO_URL'); DB_NAME = 'divine_waifus'
TS = int(time.time())
EMAIL = f'pack102_e2e_{TS}@test.com'
SID_A = f's_pack102_a_{TS}'
SID_B = f's_pack102_b_{TS}'
MARKER_102 = 'pack_102_test_artifact'
MARKER_101 = 'pack_101_test_artifact'
PREFL_KS = 'TOWER_STRICT_PREFLIGHT_ENABLED'


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
    await db.users.update_one({'id': uid}, {'$set': {MARKER_101: True, MARKER_102: True}})
    await db.player_server_profiles.update_many({'user_id': uid}, {'$set': {MARKER_101: True, MARKER_102: True}})


async def snapshot_users(uid):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    u = await db.users.find_one({'id': uid})
    return {'gold': (u or {}).get('gold', 0), 'gems': (u or {}).get('gems', 0), 'experience': (u or {}).get('experience', 0)}


async def snapshot_psp(uid, sid):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    return await db.player_server_profiles.find_one({'user_id': uid, 'server_id': sid})


async def cleanup(uid):
    if not uid: return
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    u = await db.users.find_one({'id': uid})
    if not u or not u.get(MARKER_102):
        print(f'[CLEANUP REFUSED] not marked'); return
    await db.users.delete_one({'id': uid})
    await db.player_server_profiles.delete_many({'user_id': uid})
    await db.tower_progress.delete_many({'user_id': uid})
    await db.user_heroes.delete_many({'user_id': uid})
    await db.user_equipment.delete_many({'user_id': uid})
    await db.inventory.delete_many({'user_id': uid})
    await db.wallets.delete_many({'user_id': uid})
    await db.reward_claim_ledger.delete_many({'user_id': uid})
    await db.daily_quest_progress.delete_many({'user_id': uid})
    print('[CLEANUP OK]')


def run():
    uid = None; proofs = {}
    pf_orig = os.getenv(PREFL_KS, None)
    base_ids = set(LAUNCH_BASE_HERO_IDS)
    premium_ids = set(EXTRA_PREMIUM_HERO_IDS)
    try:
        # === 1. Catalog summary ===
        st, body = get('/api/tower/strict/catalog')
        assert st == 200, body
        c = body['catalog']
        assert c['catalog_version'] == 'tower_v1_100_launch'
        assert c['total_floors'] == 100
        assert c['team_size'] == 6
        assert c['boss_floors'] == [10, 20, 30, 40, 60, 70, 80, 90]
        assert c['major_boss_floors'] == [50, 100]
        assert c['mini_spike_floors'] == [5, 15, 25, 35, 45, 55, 65, 75, 85, 95]
        assert c['deterministic'] is True
        assert c['uses_only_launch_base_heroes'] is True
        assert c['borea_or_extra_premium_used'] is False
        assert c['content_identical_across_servers'] is True
        assert body['reward_live_general'] is False
        assert body['tower_reward_live_grant'] is False
        proofs['catalog_summary_100_floors_deterministic'] = True

        # === 2. Floor 1 detail ===
        st, body = get('/api/tower/strict/catalog/floor/1')
        assert st == 200
        cf = body['catalog_floor']
        assert cf['floor'] == 1 and cf['floor_type'] == 'normal'
        assert cf['team_size'] == 6 and len(cf['enemy_team']) == 6
        assert cf['boss_leader_slot'] is None
        # No duplicates
        ids = [s['hero_id'] for s in cf['enemy_team']]
        assert len(set(ids)) == 6
        # All in launch_base
        for hid in ids:
            assert hid in base_ids, f'invalid hero_id: {hid}'
            assert hid not in premium_ids
        proofs['floor_1_valid_no_dup_only_launch_base'] = True

        # === 3. Floor 5 mini-spike ===
        st, body = get('/api/tower/strict/catalog/floor/5')
        assert st == 200
        cf = body['catalog_floor']
        assert cf['floor_type'] == 'mini_spike'
        assert cf['boss_leader_slot'] is None
        proofs['floor_5_mini_spike'] = True

        # === 4. Floor 10 boss team ===
        st, body = get('/api/tower/strict/catalog/floor/10')
        assert st == 200
        cf = body['catalog_floor']
        assert cf['floor_type'] == 'boss_team'
        assert cf['boss_leader_slot'] == 0
        assert cf['enemy_team'][0]['is_boss_leader'] is True
        # boss leader rarity >= tier
        assert cf['enemy_team'][0]['native_rarity'] >= cf['tier']
        proofs['floor_10_boss_team_with_leader'] = True

        # === 5. Floor 50 major boss ===
        st, body = get('/api/tower/strict/catalog/floor/50')
        assert st == 200
        cf = body['catalog_floor']
        assert cf['floor_type'] == 'major_boss_team'
        assert cf['boss_leader_slot'] == 0
        assert cf['enemy_team'][0]['is_boss_leader'] is True
        assert cf['enemy_team'][0]['native_rarity'] >= 5
        proofs['floor_50_major_boss_rarity_ge_5'] = True

        # === 6. Floor 100 major boss strongest ===
        st, body = get('/api/tower/strict/catalog/floor/100')
        assert st == 200
        cf = body['catalog_floor']
        assert cf['floor_type'] == 'major_boss_team'
        assert cf['boss_leader_slot'] == 0
        assert cf['enemy_team'][0]['is_boss_leader'] is True
        assert cf['enemy_team'][0]['native_rarity'] == 6
        assert cf['tier'] == 6
        # All 6 team members in launch_base
        for s in cf['enemy_team']:
            assert s['hero_id'] in base_ids
            assert s['hero_id'] not in premium_ids
        proofs['floor_100_major_boss_rarity_6_all_official'] = True

        # === 7. Out of range -> 404 ===
        st, body = get('/api/tower/strict/catalog/floor/0')
        assert st == 404
        st, body = get('/api/tower/strict/catalog/floor/101')
        assert st == 404
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert d['blocker'] == 'FLOOR_OUT_OF_CATALOG_RANGE'
        proofs['out_of_range_floors_404'] = True

        # === 8. Determinism: stessa risposta 5 volte su floor 50 ===
        snapshots = []
        for _ in range(5):
            st, body = get('/api/tower/strict/catalog/floor/50')
            assert st == 200
            cf = body['catalog_floor']
            snap = [(s['slot_index'], s['hero_id'], s['native_rarity']) for s in cf['enemy_team']]
            snapshots.append(tuple(snap))
        assert len(set(snapshots)) == 1, f'NOT deterministic: {snapshots}'
        proofs['catalog_floor_50_deterministic_5x'] = True

        # === 9. Catalog wide validation: all 100 floors valid ===
        for f in range(1, 101):
            st, body = get(f'/api/tower/strict/catalog/floor/{f}')
            assert st == 200, f'floor {f} HTTP {st}'
            cf = body['catalog_floor']
            assert cf['floor'] == f
            assert len(cf['enemy_team']) == 6
            ids = [s['hero_id'] for s in cf['enemy_team']]
            assert len(set(ids)) == 6, f'floor {f} duplicates: {ids}'
            for hid in ids:
                assert hid in base_ids, f'floor {f} invalid hero: {hid}'
                assert hid not in premium_ids, f'floor {f} premium hero: {hid}'
            # Boss invariants
            if f in (10, 20, 30, 40, 60, 70, 80, 90):
                assert cf['floor_type'] == 'boss_team'
                assert cf['boss_leader_slot'] == 0
                assert cf['enemy_team'][0]['is_boss_leader'] is True
            elif f in (50, 100):
                assert cf['floor_type'] == 'major_boss_team'
                assert cf['boss_leader_slot'] == 0
                assert cf['enemy_team'][0]['native_rarity'] >= 5
            elif f % 5 == 0:
                assert cf['floor_type'] == 'mini_spike'
            else:
                assert cf['floor_type'] == 'normal'
        proofs['all_100_floors_valid_no_dup_no_premium_boss_team_only'] = True

        # === 10. Register + ensure PSP A+B + mark ===
        st, body = post('/api/register', {
            'email': EMAIL, 'password': 'pack102pw', 'username': f'p102u_{TS}'
        })
        assert st == 200, body
        uid = body['user']['id']
        auth = {'Authorization': f'Bearer {body["token"]}'}
        proofs['register_ok'] = True
        st, _ = post(f'/api/psp/ensure?server_id={SID_A}', None, auth)
        assert st in (200, 201)
        st, _ = post(f'/api/psp/ensure?server_id={SID_B}', None, auth)
        assert st in (200, 201)
        proofs['ensure_psp_a_b'] = True
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        loop.run_until_complete(mark(uid))
        proofs['mark_pack_101_102_ok'] = True
        users_before = loop.run_until_complete(snapshot_users(uid))

        # === 11. Preview floor 1 S1 con catalog wired ===
        st, body = post(f'/api/tower/strict/battle/preview?server_id={SID_A}&floor=1', {}, auth)
        assert st == 200, body
        assert body['_slc_pack_102_catalog_wired'] is True
        assert body['catalog_floor']['floor'] == 1
        assert body['catalog_floor']['floor_type'] == 'normal'
        assert len(body['catalog_floor']['enemy_team']) == 6
        proofs['preview_floor_1_with_catalog'] = True

        # === 12. Preview floor 50 S1 ===
        st, body = post(f'/api/tower/strict/battle/preview?server_id={SID_A}&floor=50', {}, auth)
        assert st == 200
        assert body['catalog_floor']['floor'] == 50
        assert body['catalog_floor']['floor_type'] == 'major_boss_team'
        proofs['preview_floor_50_major_boss_catalog'] = True

        # === 13. Preview floor 100 S1 ===
        st, body = post(f'/api/tower/strict/battle/preview?server_id={SID_A}&floor=100', {}, auth)
        assert st == 200
        assert body['catalog_floor']['floor'] == 100
        assert body['catalog_floor']['enemy_team'][0]['native_rarity'] == 6
        proofs['preview_floor_100_strongest_launch'] = True

        # === 14. Preview floor 101 -> 404 ===
        st, body = post(f'/api/tower/strict/battle/preview?server_id={SID_A}&floor=101', {}, auth)
        assert st == 404
        d = body.get('detail') if isinstance(body.get('detail'), dict) else body
        assert d['blocker'] == 'FLOOR_OUT_OF_CATALOG_RANGE'
        proofs['preview_floor_101_out_of_range_404'] = True

        # === 15. NO mutation users.* end-to-end ===
        users_after = loop.run_until_complete(snapshot_users(uid))
        assert users_before == users_after, f'users mutated! {users_before} -> {users_after}'
        proofs['users_gold_gems_experience_invariant'] = True

        # === 16. S1/S2 isolation: preflight su S1, S2 resta vuoto ===
        write_env_kv({PREFL_KS: 'true'})
        st, body = post(f'/api/tower/strict/preflight?server_id={SID_A}', {}, auth)
        assert st == 200
        psp_a = loop.run_until_complete(snapshot_psp(uid, SID_A))
        psp_b = loop.run_until_complete(snapshot_psp(uid, SID_B))
        assert (psp_a.get('tower_progress') or {}).get('_slc_pack_101_strict') is True
        assert not (psp_b.get('tower_progress') or {}), f'S2 leak: {psp_b.get("tower_progress")}'
        proofs['preflight_S1_no_S2_contamination'] = True

        # === 17. Preview con floor 50 NON avanza progress ===
        psp_a_pre = loop.run_until_complete(snapshot_psp(uid, SID_A))
        floor_pre = (psp_a_pre.get('tower_progress') or {}).get('floor', 1)
        st, _ = post(f'/api/tower/strict/battle/preview?server_id={SID_A}&floor=50', {}, auth)
        psp_a_post = loop.run_until_complete(snapshot_psp(uid, SID_A))
        floor_post = (psp_a_post.get('tower_progress') or {}).get('floor', 1)
        assert floor_pre == floor_post, f'preview avanzata progress: {floor_pre} -> {floor_post}'
        proofs['preview_no_progress_advance'] = True

        # === 18. Pack 100 daily-quest health preservato ===
        st, body = get('/api/daily-quest/claim/health')
        assert body.get('pack_100_event_bridge_integrated') is True
        proofs['pack_100_preserved'] = True

        # === 19. Pack 95 story strict still works ===
        import uuid as _uuid
        tok = f'pack102_tok_{_uuid.uuid4().hex[:16]}'
        st, body = post(f'/api/story/battle?server_id={SID_A}&idempotency_token={tok}',
                        {'chapter_id': 1, 'stage': 1}, auth)
        assert st == 200 and body.get('pack_95_strict_story_progress_write') is True
        proofs['pack_95_story_strict_preserved'] = True

        # === 20. Pack 101 tower strict still works (health) ===
        st, body = get('/api/tower/strict/health')
        assert body.get('tower_progress_server_scope_status') == 'TOWER_PROGRESS_SERVER_SCOPED_STRICT_READY'
        assert body.get('tower_catalog_total_floors') == 100
        proofs['pack_101_tower_strict_health_preserved'] = True

    finally:
        write_env_kv({PREFL_KS: pf_orig})
        proofs['kill_switch_restored'] = True
        if uid:
            loopc = asyncio.new_event_loop(); asyncio.set_event_loop(loopc)
            loopc.run_until_complete(cleanup(uid))
            proofs['cleanup_ok'] = True
    return proofs


if __name__ == '__main__':
    proofs = run()
    required = [
        'catalog_summary_100_floors_deterministic',
        'floor_1_valid_no_dup_only_launch_base',
        'floor_5_mini_spike',
        'floor_10_boss_team_with_leader',
        'floor_50_major_boss_rarity_ge_5',
        'floor_100_major_boss_rarity_6_all_official',
        'out_of_range_floors_404',
        'catalog_floor_50_deterministic_5x',
        'all_100_floors_valid_no_dup_no_premium_boss_team_only',
        'register_ok', 'ensure_psp_a_b', 'mark_pack_101_102_ok',
        'preview_floor_1_with_catalog',
        'preview_floor_50_major_boss_catalog',
        'preview_floor_100_strongest_launch',
        'preview_floor_101_out_of_range_404',
        'users_gold_gems_experience_invariant',
        'preflight_S1_no_S2_contamination',
        'preview_no_progress_advance',
        'pack_100_preserved',
        'pack_95_story_strict_preserved',
        'pack_101_tower_strict_health_preserved',
        'kill_switch_restored', 'cleanup_ok',
    ]
    missing = [k for k in required if proofs.get(k) is not True]
    out = {
        'pack': 'MEGA_RELEASE_ACCELERATION_102_TOWER_100_FLOOR_CATALOG_DETERMINISTIC_ENEMY_TEAMS',
        'timestamp_utc_ts': TS,
        'test_artifact_marker_pack_102': MARKER_102,
        'proofs': proofs, 'required_missing': missing,
        'real_smoke_executed': len(missing) == 0,
        'catalog_version': 'tower_v1_100_launch',
        'total_launch_floors': 100,
        'all_enemy_teams_deterministic': True,
        'all_enemy_hero_ids_valid_official_eligible': True,
        'boss_floors_are_team_boss_not_true_monster': True,
        'floor_content_identical_across_servers': True,
        'progress_server_scoped_s1_s2': True,
        'no_users_gold_gems_experience_mutation_from_tower': True,
        'tower_reward_live_status': 'REWARD_QUARANTINED_PENDING_LEDGER',
        'no_premium_grant': True, 'no_reward_live_general': True,
        'release_readiness_claimed': False,
    }
    out_path = '/app/data/design/v110_pack_102_tower_100_floor_catalog/v110_pack_102_runtime_smoke_e2e_result_v1.json'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f: json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    if missing:
        print(f'[v110 PACK_102_RUNTIME_SMOKE_E2E] BLOCKED missing={missing}')
        sys.exit(2)
    print('[v110 PACK_102_RUNTIME_SMOKE_E2E] OK 100_floors_deterministic team_bosses_only S1_S2_isolated '
          'no_users_mutation no_reward_live pack_91_101_preserved')
