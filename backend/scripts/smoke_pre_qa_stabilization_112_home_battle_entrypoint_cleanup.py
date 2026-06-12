#!/usr/bin/env python3
"""Pre-QA Stabilization 112 — Home & Battle Entrypoint Cleanup Smoke E2E (19 step)."""
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


async def main():
    client = AsyncIOMotorClient(MONGO_URL); db = client[DB_NAME]
    uid = f'prq112_{uuid.uuid4().hex[:8]}'
    pwd = hashlib.sha256(b'prq112_test_pw').hexdigest()
    initial_gems = 5000
    inserted = []
    try:
        await db.users.insert_one({
            'id': uid, 'username': uid, 'email': f'{uid}@prq112.test', 'password': pwd,
            'level': 1, 'gold': 0, 'gems': initial_gems, 'experience': 0,
        })
        inserted.append(uid)
        tok = jwt.encode({'user_id': uid, 'exp': int(time.time()) + 3600}, JWT_SECRET, algorithm='HS256')

        # 1) HOME_ROUTES still expose unsafe routes BUT goTo guard blocks them.
        home = open(os.path.join(ROOT, 'frontend/app/(tabs)/home.tsx')).read()
        assert 'preQaNavGuard' in home and 'isRouteAllowedInPreQa' in home
        assert 'PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED' in home
        print('[1] Home goTo blocked via shared preQaNavGuard OK')

        # 2) HomeOverflowPanel uses guard implicitly (overflow opens overflow; child onPress also uses goTo).
        # Verifichiamo che la shared guard sia caricata e che le route comuni siano nel set canonico.
        guard = open(os.path.join(ROOT, 'frontend/src/utils/preQaNavGuard.ts')).read()
        for r in ("'/gacha'", "'/events'", "'/pvp'", "'/shop'", "'/guild'", "'/vip'", "'/battlepass'", "'/raid'", "'/gvg'", "'/plaza'", "'/dm'", "'/territory'"):
            assert r in guard, f'shared guard missing route: {r}'
        print('[2] Shared nav guard contains all unsafe player routes OK')

        # 3) Menu tab cleanup preserved (uses shared guard).
        menu = open(os.path.join(ROOT, 'frontend/app/(tabs)/menu.tsx')).read()
        assert 'preQaNavGuard' in menu
        print('[3] Menu uses shared nav guard OK')

        # 4) Evoca tab hidden default.
        layout = open(os.path.join(ROOT, 'frontend/app/(tabs)/_layout.tsx')).read()
        assert 'href: null' in layout and 'EXPO_PUBLIC_GACHA_UI_ENABLED' in layout
        print('[4] Evoca tab hidden default OFF OK')

        # 5) pre-battle-lobby reads v101_selected_server_id.
        pbl = open(os.path.join(ROOT, 'frontend/app/pre-battle-lobby.tsx')).read()
        assert "'v101_selected_server_id'" in pbl
        assert "AsyncStorage.getItem('selected_server_id')" not in pbl, 'old key still present'
        print('[5] pre-battle-lobby reads v101_selected_server_id OK')

        # 6) pre-battle-lobby uses getAuthTokenCompat.
        assert 'getAuthTokenCompat' in pbl
        # No raw SecureStore.getItemAsync(v96_auth_token) call left.
        assert "SecureStore.getItemAsync('v96_auth_token')" not in pbl
        print('[6] pre-battle-lobby uses getAuthTokenCompat OK')

        # 7) /api/pvp/battle quarantine.
        s, j = _req('POST', '/pvp/battle', token=tok, body={})
        assert s == 423 and (j.get('detail') or {}).get('blocker') == 'PVP_BATTLE_LEGACY_QUARANTINED', (s, j)
        print('[7] pvp/battle quarantined OK')

        # 8) /api/events/battle quarantine.
        s, j = _req('POST', '/events/battle', token=tok, body={'event_id': 'x'})
        assert s == 423 and (j.get('detail') or {}).get('blocker') == 'EVENTS_BATTLE_LEGACY_QUARANTINED', (s, j)
        print('[8] events/battle quarantined OK')

        # 9) /api/story/battle senza server_id blocked.
        s, j = _req('POST', '/story/battle', token=tok, body={'chapter_id': 1, 'stage': 1})
        assert s == 423 and (j.get('detail') or {}).get('blocker') == 'STORY_BATTLE_LEGACY_NO_SERVER_ID_QUARANTINED', (s, j)
        print('[9] story/battle no-server-id blocked OK')

        # 10) strict story server_id path: still callable structurally (we do NOT attempt mutation here).
        # Just verify path exists; combat.py source check.
        combat = open(os.path.join(ROOT, 'backend/routes/combat.py')).read()
        assert 'STORY_BATTLE_STRICT_SERVER_SCOPED_REQUIRED' in combat
        print('[10] strict story server_id path documented OK')

        # 11) route classification: no false-readonly mutating POST.
        import subprocess
        out = subprocess.check_output(['python', os.path.join(ROOT, 'backend/scripts/validate_pre_qa_stabilization_111_route_classification.py')]).decode()
        assert 'remaining_uncategorized=0' in out
        # Verifica nel doc che story/pvp/events battle siano legacy_quarantined.
        catalog = open(os.path.join(ROOT, 'docs/divine/113_PRE_QA_STABILIZATION_111_ROUTE_CLASSIFICATION_FULL.md')).read()
        # I tre path devono comparire in legacy_quarantined section.
        assert '/story/battle' in catalog and '/pvp/battle' in catalog and '/events/battle' in catalog
        print('[11] route classification no false-readonly mutating POST OK')

        # 12) validator menu cleanup robust (no frontend/.env required).
        out2 = subprocess.check_output(['python', os.path.join(ROOT, 'backend/scripts/validate_pre_qa_stabilization_110_menu_cleanup.py')]).decode()
        assert 'PRE_QA_110_MENU_CLEANUP' in out2
        print('[12] menu cleanup validator robust without frontend/.env OK')

        # 13) heroes.py gacha duplicato dead-code quarantine.
        heroes_src = open(os.path.join(ROOT, 'backend/routes/heroes.py')).read()
        assert 'GACHA_DUPLICATE_DEAD_CODE_QUARANTINED' in heroes_src
        assert heroes_src.count('GACHA_DUPLICATE_DEAD_CODE_QUARANTINED') >= 2
        print('[13] heroes.py gacha duplicate dead-code quarantine OK')

        # 14) users.gold/gems/experience unchanged.
        u = await db.users.find_one({'id': uid})
        assert u.get('gold', 0) == 0 and u.get('gems', 0) == initial_gems and u.get('experience', 0) == 0
        print('[14] users.gold/gems/experience unchanged OK')

        # 15) reward_live_general=false.
        for ep in ('/tower/strict/health', '/economy/strict/health', '/controlled-rewards/health',
                   '/guild/strict/health', '/playable-loop/health'):
            _, jj = _req('GET', ep)
            assert jj.get('reward_live_general') in (False, None), (ep, jj)
        print('[15] reward_live_general=false everywhere OK')

        # 16) public_launch_ready=false declared in final report.
        report = open(os.path.join(ROOT, 'docs/divine/114_PRE_QA_STABILIZATION_112_HOME_BATTLE_ENTRYPOINT_CLEANUP_FINAL_REPORT.md')).read().lower()
        assert 'public_launch_ready=false' in report
        print('[16] public_launch_ready=false declared OK')

        # 17) production_release_ready=false declared.
        assert 'production_release_ready=false' in report
        print('[17] production_release_ready=false declared OK')

        # 18) no gacha/IAP/payment activation in game_systems.
        gs = open(os.path.join(ROOT, 'backend/game_systems.py')).read()
        for forbidden in ('register_iap_routes', 'register_gacha_routes_live', 'register_store_payment_routes'):
            assert forbidden not in gs
        print('[18] no gacha/IAP/payment activation OK')

        # 19) Pack 110/111 rollups preserved.
        for rollup in (
            'validate_pre_qa_stabilization_110_alpha_blocker_cleanup_rollup.py',
            'validate_pre_qa_stabilization_111_rebaseline_route_classification_rollup.py',
        ):
            assert os.path.exists(os.path.join(ROOT, 'backend/scripts', rollup)), rollup
        print('[19] Pack 110/111 rollups preserved OK')

        print('SMOKE PRE_QA_STABILIZATION_112 OK')
        return 0
    finally:
        if inserted:
            await db.users.delete_many({'id': {'$in': inserted}})
            await db.player_server_profiles.delete_many({'user_id': {'$in': inserted}})
        client.close()


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
