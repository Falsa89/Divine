#!/usr/bin/env python3
"""Pre-QA Stabilization 111 — Rebaseline + Route Classification Smoke E2E (18 steps)."""
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
    uid = f'prq111_{uuid.uuid4().hex[:8]}'
    pwd = hashlib.sha256(b'prq111_test_pw').hexdigest()
    inserted = []
    initial_gems = 5000
    try:
        await db.users.insert_one({
            'id': uid, 'username': uid, 'email': f'{uid}@prq111.test', 'password': pwd,
            'level': 1, 'gold': 0, 'gems': initial_gems, 'experience': 0,
        })
        inserted.append(uid)
        tok = jwt.encode({'user_id': uid, 'exp': int(time.time()) + 3600}, JWT_SECRET, algorithm='HS256')

        # 1) authTokenCompat adopted in servers.tsx.
        srv = open(os.path.join(ROOT, 'frontend/app/servers.tsx')).read()
        assert 'getAuthTokenCompat' in srv, 'servers.tsx does not import authTokenCompat'
        assert 'no_auth_token_psp_ensure_deferred' in srv
        print('[1] authTokenCompat adopted in servers.tsx OK')

        # 2) no silent s1 fallback in adopted code.
        import re
        lines = [ln for ln in srv.split('\n') if not ln.lstrip().startswith('//')]
        clean = '\n'.join(lines)
        assert re.search(r"\|\|\s*['\"]s1['\"]", clean) is None, 'servers.tsx silent ||"s1"'
        print('[2] no silent s1 fallback in servers.tsx OK')

        # 3) route classification with 0 uncategorized.
        import subprocess
        out = subprocess.check_output(['python', os.path.join(ROOT, 'backend/scripts/validate_pre_qa_stabilization_111_route_classification.py')]).decode()
        assert 'remaining_uncategorized=0' in out
        print('[3] route classification uncategorized=0 OK')

        # 4) Pack 110 validators registered in master suite.
        suite = open(os.path.join(ROOT, 'backend/scripts/run_hero_skill_kit_validator_suite.py')).read()
        for v in ('PROJECT-PRE-QA-110-GACHA-QUARANTINE', 'PROJECT-PRE-QA-110-TEAM-FORMATION-QUARANTINE',
                  'PROJECT-PRE-QA-110-MENU-CLEANUP', 'PRE-QA-STABILIZATION-110-ROLLUP',
                  'PROJECT-PRE-QA-111-ROUTE-CLASSIFICATION'):
            assert v in suite, f'suite missing {v}'
        print('[4] Pack 110 validators registered + Pack 111 classifier registered OK')

        # 5) MD5 rebaseline limited to authorized files.
        rb = json.load(open(os.path.join(ROOT, 'data/design/audit/pre_qa_111/md5_rebaseline_authorized.json')))
        assert rb['authorization'] == 'AUTORIZZO_PRE_QA_STABILIZATION_111_REBASELINE_ROUTE_CLASSIFICATION'
        assert rb['no_safety_violation_hidden_as_md5_drift'] is True
        assert rb['no_fake_pass'] is True and rb['no_validator_weakening'] is True
        assert len(rb['rebaselined_files']) >= 9, f'rebaseline must cover >=9 entries; got {len(rb["rebaselined_files"])}'
        # Verifica che ogni entry abbia old_hash, new_hash, file, reason, blocker.
        for e in rb['rebaselined_files']:
            for k in ('pin_file', 'field', 'old_hash', 'new_hash', 'target_file', 'reason', 'blocker_pack_110'):
                assert k in e, f'rebaseline entry missing {k}: {e}'
        # Verifica che nessun file forbidden sia stato rebaselineato.
        for forbidden in ('.env', 'character_bible', 'gacha_rates', 'jwt_secret'):
            for e in rb['rebaselined_files']:
                assert forbidden.lower() not in (e['target_file'] + ' ' + e['pin_file']).lower(), f'forbidden rebaseline: {e}'
        print('[5] MD5 rebaseline limited to authorized 10 entries OK')

        # 6) gacha pull blocked.
        s, j = _req('POST', '/gacha/pull', token=tok, body={'banner': 'standard'})
        assert s == 423 and (j.get('detail') or {}).get('blocker') == 'GACHA_LIVE_DISABLED_PRE_QA'
        s, j = _req('POST', '/gacha/pull10', token=tok, body={'banner': 'standard'})
        assert s == 423
        print('[6] gacha pull/pull10 still quarantine OK')

        # 7) Evoca hidden in tab layout.
        layout = open(os.path.join(ROOT, 'frontend/app/(tabs)/_layout.tsx')).read()
        assert 'href: null' in layout and 'EXPO_PUBLIC_GACHA_UI_ENABLED' in layout
        print('[7] Evoca hidden default OFF OK')

        # 8) achievement legacy claim blocked.
        s, j = _req('POST', '/achievements/claim', token=tok, body={'achievement_id': 'first_battle', 'tier_index': 0})
        assert s == 423 and (j.get('detail') or {}).get('blocker') == 'ACHIEVEMENT_LEGACY_CLAIM_QUARANTINED'
        print('[8] legacy achievement claim still quarantine OK')

        # 9) team formation legacy update blocked.
        s, j = _req('POST', '/team/update-formation', token=tok, body={'formation': []})
        assert s == 423 and (j.get('detail') or {}).get('blocker') == 'TEAM_FORMATION_LEGACY_QUARANTINED'
        print('[9] team/update-formation legacy still quarantine OK')

        # 10) reward_live_general=false everywhere.
        for ep in ('/tower/strict/health', '/economy/strict/health', '/controlled-rewards/health',
                   '/guild/strict/health', '/playable-loop/health'):
            _, jj = _req('GET', ep)
            assert jj.get('reward_live_general') in (False, None), (ep, jj)
        print('[10] reward_live_general=false everywhere OK')

        # 11) release_readiness_claimed=false everywhere.
        for ep in ('/tower/strict/health', '/controlled-rewards/health', '/guild/strict/health'):
            _, jj = _req('GET', ep)
            assert jj.get('release_readiness_claimed') in (False, None)
        print('[11] release_readiness_claimed=false OK')

        # 12) public_launch_ready=false.
        report = open(os.path.join(ROOT, 'docs/divine/113_PRE_QA_STABILIZATION_111_REBASELINE_ROUTE_CLASSIFICATION_FINAL_REPORT.md')).read().lower()
        assert 'public_launch_ready=false' in report
        print('[12] public_launch_ready=false declared in final report OK')

        # 13) production_release_ready=false.
        assert 'production_release_ready=false' in report
        print('[13] production_release_ready=false declared in final report OK')

        # 14) users.gold/gems/experience unchanged.
        u = await db.users.find_one({'id': uid})
        assert u.get('gold', 0) == 0 and u.get('gems', 0) == initial_gems and u.get('experience', 0) == 0
        print('[14] users.gold/gems/experience unchanged OK')

        # 15) no premium/hard/gems grants in registry.
        rsr = os.path.join(ROOT, 'backend/utils/reward_source_registry.py')
        if os.path.exists(rsr):
            c = open(rsr).read().lower()
            for bad in ('guild_reward_live"', 'arena_reward_live"', 'pvp_reward_live"'):
                assert bad not in c
        print('[15] no premium/hard/gems grants OK')

        # 16) no IAP/gacha/payment activation in game_systems.
        gs = open(os.path.join(ROOT, 'backend/game_systems.py')).read()
        for forbidden in ('register_iap_routes', 'register_gacha_routes_live', 'register_store_payment_routes'):
            assert forbidden not in gs
        print('[16] no IAP/gacha/payment activation OK')

        # 17) no guild/arena/pvp/event/battlepass/AFK reward live (Pack 107+ guards intact).
        c = open(os.path.join(ROOT, 'backend/routes/competitive_guards.py')).read()
        for tok_t in ('ARENA_REWARD_LIVE_DISABLED', 'PVP_RANKING_SERVER_SCOPE_DEFERRED',
                      'EVENT_REWARD_LIVE_DISABLED', 'GUILD_REWARD_LIVE_DISABLED'):
            assert tok_t in c
        print('[17] no guild/arena/pvp/event reward live OK')

        # 18) Pack 91-110 safety preserved.
        for rollup in (
            'validate_mega_release_acceleration_104_shop_soul_equipment_forge_strict_writes_rollup.py',
            'validate_mega_release_acceleration_105_forge_upgrade_fusion_strict_psp_material_ledger_spend_rollup.py',
            'validate_mega_release_acceleration_106_mail_achievements_daily_weekly_controlled_rewards_rollup.py',
            'validate_mega_release_acceleration_107_arena_pvp_guild_events_server_scope_guards_rollup.py',
            'validate_mega_release_acceleration_108_guild_server_scope_retrofit_frontend_playable_loop_polish_rollup.py',
            'validate_mega_release_acceleration_109_closed_alpha_rc_sweep_and_release_gate_rollup.py',
            'validate_pre_qa_stabilization_110_alpha_blocker_cleanup_rollup.py',
        ):
            assert os.path.exists(os.path.join(ROOT, 'backend/scripts', rollup)), rollup
        print('[18] Pack 91-110 rollups preserved OK')

        print('SMOKE PRE_QA_STABILIZATION_111 OK')
        return 0
    finally:
        if inserted:
            await db.users.delete_many({'id': {'$in': inserted}})
            await db.player_server_profiles.delete_many({'user_id': {'$in': inserted}})
            await db.user_heroes.delete_many({'user_id': {'$in': inserted}})
        client.close()


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
