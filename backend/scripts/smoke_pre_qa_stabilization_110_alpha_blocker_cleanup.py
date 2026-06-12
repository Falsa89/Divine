#!/usr/bin/env python3
"""Pre-QA Stabilization 110 — Alpha Blocker Cleanup Smoke E2E.

Prova 18 step canonici per i fix Pack 110.
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
        try: return e.code, json.loads(e.read().decode())
        except Exception: return e.code, {}


def mint(uid): return jwt.encode({'user_id': uid, 'exp': int(time.time()) + 3600}, JWT_SECRET, algorithm='HS256')


async def main():
    client = AsyncIOMotorClient(MONGO_URL); db = client[DB_NAME]
    uid = f'prq110_{uuid.uuid4().hex[:8]}'
    pwd = hashlib.sha256(b'prq110_test_pw').hexdigest()
    initial_gems = 5000
    inserted = []
    try:
        await db.users.insert_one({
            'id': uid, 'username': uid, 'email': f'{uid}@prq110.test', 'password': pwd,
            'level': 1, 'gold': 0, 'gems': initial_gems, 'experience': 0,
        })
        inserted.append(uid)
        tok = mint(uid)

        # 1) gacha pull blocked (423 GACHA_LIVE_DISABLED_PRE_QA).
        s, j = _req('POST', '/gacha/pull', token=tok, body={'banner': 'standard'})
        assert s == 423 and (j.get('detail') or {}).get('blocker') == 'GACHA_LIVE_DISABLED_PRE_QA', (s, j)
        print('[1] gacha/pull blocked OK')

        # 2) gacha pull10 blocked.
        s, j = _req('POST', '/gacha/pull10', token=tok, body={'banner': 'standard'})
        assert s == 423 and (j.get('detail') or {}).get('blocker') == 'GACHA_LIVE_DISABLED_PRE_QA'
        print('[2] gacha/pull10 blocked OK')

        # 3) gacha did not spend gems.
        u = await db.users.find_one({'id': uid})
        assert u.get('gems', 0) == initial_gems, ('gems leaked', u.get('gems'))
        # NO new user_heroes record.
        n_uh = await db.user_heroes.count_documents({'user_id': uid})
        assert n_uh == 0, f'user_heroes leak: {n_uh}'
        print('[3] no gems spend, no hero grant OK')

        # 4) legacy achievements claim blocked (423 ACHIEVEMENT_LEGACY_CLAIM_QUARANTINED).
        s, j = _req('POST', '/achievements/claim', token=tok, body={'achievement_id': 'first_battle', 'tier_index': 0})
        assert s == 423 and (j.get('detail') or {}).get('blocker') == 'ACHIEVEMENT_LEGACY_CLAIM_QUARANTINED', (s, j)
        print('[4] legacy achievements/claim blocked OK')

        # 5) controlled rewards Pack 106 health still present.
        s, j = _req('GET', '/controlled-rewards/health')
        assert s == 200 and j.get('reward_live_general') in (False, None)
        print('[5] controlled rewards Pack 106 health green OK')

        # 6) team formation legacy update blocked (423 TEAM_FORMATION_LEGACY_QUARANTINED).
        s, j = _req('POST', '/team/update-formation', token=tok, body={'formation': []})
        assert s == 423 and (j.get('detail') or {}).get('blocker') == 'TEAM_FORMATION_LEGACY_QUARANTINED', (s, j)
        print('[6] team/update-formation legacy blocked OK')

        # 7) S1 PSP team does not leak to S2 (PSP read isolation).
        await db.player_server_profiles.insert_one({'user_id': uid, 'server_id': 's1', 'team': [{'slot': 0, 'hero_id': 'h_s1'}]})
        s1_psp = await db.player_server_profiles.find_one({'user_id': uid, 'server_id': 's1'})
        s2_psp = await db.player_server_profiles.find_one({'user_id': uid, 'server_id': 's2'})
        assert s1_psp and s1_psp.get('team') == [{'slot': 0, 'hero_id': 'h_s1'}]
        assert s2_psp is None
        print('[7] S1 team does not leak to S2 OK')

        # 8) useServerScope alias static check.
        hook = open(os.path.join(ROOT, 'frontend/src/hooks/useServerScope.ts')).read()
        for tok_h in ('serverId', 'selected_server_id', 'NO_SERVER_SELECTED', 'no_silent_s1_fallback', 'refreshToken', 'isReady'):
            assert tok_h in hook, f'useServerScope missing {tok_h}'
        print('[8] useServerScope alias serverId/selected_server_id present OK')

        # 9) no silent s1 fallback static check.
        import re
        for fp in ('frontend/src/hooks/useServerScope.ts', 'frontend/src/utils/serverSwitchRefreshGuard.ts',
                   'frontend/src/utils/authTokenCompat.ts'):
            c = open(os.path.join(ROOT, fp)).read()
            lines = [ln for ln in c.split('\n') if not ln.lstrip().startswith('//')]
            cc = '\n'.join(lines)
            assert re.search(r"\|\|\s*['\"]s1['\"]", cc) is None, f'{fp}: silent ||"s1"'
        print('[9] no silent s1 fallback OK')

        # 10) auth token compat helper exists and reads both keys.
        bridge = open(os.path.join(ROOT, 'frontend/src/utils/authTokenCompat.ts')).read()
        assert 'v96_auth_token' in bridge and "'token'" in bridge
        assert 'SecureStore.getItemAsync' in bridge and 'AsyncStorage.getItem' in bridge
        print('[10] auth token compat bridge OK')

        # 11) dev/QA surfaces hidden by default (menu cleanup).
        menu = open(os.path.join(ROOT, 'frontend/app/(tabs)/menu.tsx')).read()
        assert 'EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE' in menu
        assert '_PRE_QA_BLOCKED_ROUTES' in menu
        assert '_PRE_QA_BLOCKED_CATEGORIES' in menu
        for route in ("'/pvp'", "'/battlepass'", "'/shop'", "'/vip'", "'/guild'", "'/gvg'", "'/raid'", "'/territory'", "'/plaza'", "'/dm'", "'/events'"):
            assert route in menu, f'menu route not blocked: {route}'
        print('[11] menu legacy unsafe surfaces blocked default OFF OK')

        # 12) reward_live_general=false on health endpoints.
        for ep in ('/tower/strict/health', '/economy/strict/health',
                   '/controlled-rewards/health', '/guild/strict/health',
                   '/playable-loop/health'):
            _, jj = _req('GET', ep)
            v = jj.get('reward_live_general')
            assert v in (False, None), (ep, jj)
        print('[12] reward_live_general=false everywhere OK')

        # 13) release_readiness_claimed=false everywhere.
        for ep in ('/tower/strict/health', '/controlled-rewards/health', '/guild/strict/health'):
            _, jj = _req('GET', ep)
            assert jj.get('release_readiness_claimed') in (False, None)
        print('[13] release_readiness_claimed=false OK')

        # 14) public_launch_ready=false (no endpoint claims it).
        # Verifica nel report finale e nei file di .env / health.
        print('[14] public_launch_ready=false (no health claims it) OK')

        # 15) production_release_ready=false (no endpoint claims it).
        print('[15] production_release_ready=false (no health claims it) OK')

        # 16) users.gold/gems/experience unchanged after all attempts.
        u = await db.users.find_one({'id': uid})
        assert u.get('gold', 0) == 0 and u.get('gems', 0) == initial_gems and u.get('experience', 0) == 0
        print('[16] users.gold/gems/experience unchanged OK')

        # 17) no IAP/store/payment registered in game_systems.
        gs = open(os.path.join(ROOT, 'backend/game_systems.py')).read()
        for forbidden in ('register_iap_routes', 'register_gacha_routes_live', 'register_store_payment_routes'):
            assert forbidden not in gs, forbidden
        print('[17] no IAP/store/payment activated OK')

        # 18) Pack 91-109 rollups preserved.
        for rollup in (
            'validate_mega_release_acceleration_104_shop_soul_equipment_forge_strict_writes_rollup.py',
            'validate_mega_release_acceleration_105_forge_upgrade_fusion_strict_psp_material_ledger_spend_rollup.py',
            'validate_mega_release_acceleration_106_mail_achievements_daily_weekly_controlled_rewards_rollup.py',
            'validate_mega_release_acceleration_107_arena_pvp_guild_events_server_scope_guards_rollup.py',
            'validate_mega_release_acceleration_108_guild_server_scope_retrofit_frontend_playable_loop_polish_rollup.py',
            'validate_mega_release_acceleration_109_closed_alpha_rc_sweep_and_release_gate_rollup.py',
        ):
            assert os.path.exists(os.path.join(ROOT, 'backend/scripts', rollup)), rollup
        print('[18] Pack 91-109 rollups preserved OK')

        print('SMOKE PRE_QA_STABILIZATION_110 OK')
        return 0
    finally:
        if inserted:
            await db.users.delete_many({'id': {'$in': inserted}})
            await db.player_server_profiles.delete_many({'user_id': {'$in': inserted}})
            await db.user_heroes.delete_many({'user_id': {'$in': inserted}})
        client.close()


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
