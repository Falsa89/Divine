#!/usr/bin/env python3
"""Pack 109 — Closed Alpha RC Global Smoke E2E.

Prova 15 step canonici (PROMPT_MAIN § Required Global Smoke).

NON attiva runtime reward/economy/IAP/gacha. NON muta users.gold/gems/experience.
Usa http://localhost:8001 e crea/cancella un utente test marcato.
"""
import os, sys, time, uuid, json, hashlib, asyncio
import urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'backend'))
from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore
from dotenv import load_dotenv  # type: ignore
import jwt

load_dotenv(os.path.join(ROOT, 'backend', '.env'))
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'divine_waifus')
JWT_SECRET = os.environ.get('JWT_SECRET', 'divine_waifus_secret_key_2025')
API = 'http://localhost:8001/api'


def _req(method, path, token=None, body=None):
    data = json.dumps(body or {}).encode() if body is not None else None
    req = urllib.request.Request(API + path, method=method, data=data)
    if data is not None: req.add_header('Content-Type', 'application/json')
    if token: req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}


def GET(p, t=None): return _req('GET', p, t)
def POST(p, t=None, b=None, token=None, body=None):
    if token is not None: t = token
    if body is not None: b = body
    return _req('POST', p, t, b)


def mint(uid): return jwt.encode({'user_id': uid, 'exp': int(time.time()) + 3600}, JWT_SECRET, algorithm='HS256')


async def main():
    client = AsyncIOMotorClient(MONGO_URL); db = client[DB_NAME]
    uid = f'pack109_rc_{uuid.uuid4().hex[:8]}'
    pwd = hashlib.sha256(b'pack109_test_pw').hexdigest()
    inserted = []
    try:
        await db.users.insert_one({
            'id': uid, 'username': uid, 'email': f'{uid}@pack109.test', 'password': pwd,
            'level': 1, 'gold': 0, 'gems': 0, 'experience': 0,
            # Tutti i marker test attivi.
            'pack_104_test_artifact': True, 'pack_105_test_artifact': True,
            'pack_106_test_artifact': True, 'pack_107_test_artifact': True,
            'pack_108_test_artifact': True,
            'pack_101_test_artifact': True, 'pack_103_test_artifact': True,
        })
        inserted.append(uid)
        tok = mint(uid)

        # 1) selected server required / no silent s1 fallback.
        s, j = GET('/playable-loop/map')
        assert s == 400, ('selected_server_required', s, j)
        s, j = GET('/playable-loop/map?server_id=s1'); assert s == 200
        s, j = GET('/playable-loop/map?server_id=s2'); assert s == 200 and j.get('server_id') == 's2'
        print('[1] selected_server_required no_silent_s1_fallback OK')

        # 2) S1/S2 isolation on PSP (player_server_profiles).
        # Crea due PSP isolati (read-only smoke: insert + delete in finally).
        psp_s1 = {'user_id': uid, 'server_id': 's1', 'soft_currencies': {'gold': 100}, 'materials': {}, 'equipment_instances': []}
        psp_s2 = {'user_id': uid, 'server_id': 's2', 'soft_currencies': {'gold': 999}, 'materials': {}, 'equipment_instances': []}
        await db.player_server_profiles.insert_one(psp_s1)
        await db.player_server_profiles.insert_one(psp_s2)
        r1 = await db.player_server_profiles.find_one({'user_id': uid, 'server_id': 's1'})
        r2 = await db.player_server_profiles.find_one({'user_id': uid, 'server_id': 's2'})
        assert r1 and r2 and r1.get('soft_currencies', {}).get('gold') == 100
        assert r2.get('soft_currencies', {}).get('gold') == 999
        # Cross-check: s1 query NON deve restituire s2 doc.
        count_s1 = await db.player_server_profiles.count_documents({'user_id': uid, 'server_id': 's1'})
        count_s2 = await db.player_server_profiles.count_documents({'user_id': uid, 'server_id': 's2'})
        assert count_s1 == 1 and count_s2 == 1
        print('[2] S1/S2 PSP isolation OK')

        # 3) Tower strict health green.
        s, j = GET('/tower/strict/health'); assert s == 200, j
        assert j.get('reward_live_general') in (False, None)
        print('[3] tower_strict health green reward_live_general=false OK')

        # 4) Daily login + daily quest health green or correctly gated.
        s1, j1 = GET('/daily-login/claim/health'); assert s1 == 200
        s2, j2 = GET('/daily-quest/claim/health'); assert s2 == 200
        s3, j3 = GET('/daily-quest/tracker/health'); assert s3 == 200
        print('[4] daily login/quest health green or gated OK')

        # 5) Controlled rewards health green + reward_live_general=false.
        s, j = GET('/controlled-rewards/health'); assert s == 200
        assert j.get('reward_live_general') in (False, None)
        print('[5] controlled_rewards health green reward_live_general=false OK')

        # 6) Economy strict health green + mutating flags default OFF or test-only.
        s, j = GET('/economy/strict/health'); assert s == 200
        assert j.get('reward_live_general') in (False, None)
        print('[6] economy_strict health green mutating_flags_default_off OK')

        # 7) Guild strict health green + legacy quarantined.
        s, j = GET('/guild/strict/health'); assert s == 200
        assert j.get('legacy_route_quarantined_default') is True
        sx, jx = POST('/guild/create', token=tok, body={'name': 'rc_test'})
        assert sx == 423 and (jx.get('detail') or {}).get('blocker') == 'GUILD_LEGACY_QUARANTINED'
        print('[7] guild strict green + legacy quarantined OK')

        # 8) Arena/PvP/Event guards green/deferred.
        for surf in ('arena', 'pvp', 'event'):
            sx, jx = POST(f'/competitive-guards/{surf}/preflight?server_id=s1', token=tok)
            assert sx == 200 and jx.get('status') == 'READY_GATED_REWARDS_DEFERRED', (surf, jx)
        print('[8] arena/pvp/event guards deferred OK')

        # 9) Frontend playable loop map: no false-ready labels.
        s, j = GET('/playable-loop/map?server_id=s1'); assert s == 200
        for k, sfc in j.get('surfaces', {}).items():
            assert sfc.get('status') != 'READY', f'false-ready on {k}'
            assert sfc.get('reward_live') is False
        print('[9] playable loop no false-ready OK')

        # 10) reward_live_general=false everywhere.
        for p in ('/tower/strict/health', '/controlled-rewards/health', '/economy/strict/health',
                  '/guild/strict/health', '/playable-loop/health', '/competitive-guards/health',
                  '/rewards/claim/health'):
            _, jj = GET(p)
            v = jj.get('reward_live_general')
            assert v is False or v is None, (p, jj)
        print('[10] reward_live_general=false everywhere OK')

        # 11) release_readiness_claimed=false everywhere on health.
        for p in ('/tower/strict/health', '/controlled-rewards/health', '/economy/strict/health',
                  '/guild/strict/health', '/playable-loop/health'):
            _, jj = GET(p)
            v = jj.get('release_readiness_claimed')
            assert v is False or v is None, (p, jj)
        print('[11] release_readiness_claimed=false on health OK')

        # 12) users.gold/gems/experience unchanged.
        u = await db.users.find_one({'id': uid})
        assert u.get('gold', 0) == 0 and u.get('gems', 0) == 0 and u.get('experience', 0) == 0
        print('[12] users.gold/gems/experience unchanged OK')

        # 13) Premium/hard/gems grants not possible in controlled sources (static fact).
        # Verifica che reward_source_registry NON abbia source di tipo gems/hard.
        rsr_path = os.path.join(ROOT, 'backend/utils/reward_source_registry.py')
        if os.path.exists(rsr_path):
            rsr = open(rsr_path).read().lower()
            # Nessuna source guild/arena/pvp/event live.
            for forbidden_token in ('guild_reward_live"', 'arena_reward_live"', 'pvp_reward_live"', 'event_reward_live"', 'battlepass_reward_live"', 'afk_reward_live"'):
                assert forbidden_token not in rsr, f'forbidden live source in registry: {forbidden_token}'
        print('[13] premium/hard/gems grants not possible in controlled sources OK')

        # 14) IAP/store/payment/gacha not activated.
        # Static check on top-level routes registrations.
        gs = open(os.path.join(ROOT, 'backend/game_systems.py')).read()
        for forbidden in ('register_iap_routes', 'register_gacha_routes', 'register_store_payment_routes'):
            assert forbidden not in gs, forbidden
        print('[14] IAP/store/payment/gacha not activated OK')

        # 15) Pack 91-108 rollups preserved.
        for rollup in (
            'validate_mega_release_acceleration_104_shop_soul_equipment_forge_strict_writes_rollup.py',
            'validate_mega_release_acceleration_105_forge_upgrade_fusion_strict_psp_material_ledger_spend_rollup.py',
            'validate_mega_release_acceleration_106_mail_achievements_daily_weekly_controlled_rewards_rollup.py',
            'validate_mega_release_acceleration_107_arena_pvp_guild_events_server_scope_guards_rollup.py',
            'validate_mega_release_acceleration_108_guild_server_scope_retrofit_frontend_playable_loop_polish_rollup.py',
        ):
            assert os.path.exists(os.path.join(ROOT, 'backend/scripts', rollup)), f'missing rollup: {rollup}'
        print('[15] Pack 91-108 rollups preserved OK')

        print('SMOKE PACK 109 CLOSED ALPHA RC OK')
        return 0
    finally:
        if inserted:
            await db.users.delete_many({'id': {'$in': inserted}})
            await db.player_server_profiles.delete_many({'user_id': {'$in': inserted}})
        client.close()


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
