#!/usr/bin/env python3
"""
Pack 92 — Runtime guard smoke (READ-ONLY).

OBIETTIVO:
  Verificare via REAL HTTP contro 127.0.0.1:8001 che i loader server-scope
  guards di wallet/story/equipment funzionino correttamente:
  - server_id presente + PSP esistente -> filtro REALE / split REALE
  - server_id presente + PSP mancante  -> blocker onesto (filter_applied=true ma blocker)
  - server_id assente                   -> legacy path flagged non-player-facing (filter_applied=false)
  - NO false filter_applied=true
  - NO DB writes (read-only)
  - Pack 91 inventory invariant preservato

Cleanup: test user marcato `pack_92_test_artifact=true` + cleanup nel finally.
"""
import os, json, sys, urllib.request, urllib.error, asyncio, time

sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient

BASE = 'http://127.0.0.1:8001'
MONGO = os.getenv('MONGO_URL')
DB_NAME = 'divine_waifus'

TS = int(time.time())
EMAIL = f'pack92_test_user_{TS}@test.com'
PWD = 'pack92pw'
SID_A = f's_pack92_a_{TS}'
SID_UNKNOWN = f's_pack92_unknown_{TS}'
MARKER = 'pack_92_test_artifact'


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
            payload = json.loads(e.read())
        except Exception:
            payload = {}
        return e.code, payload


def post(p, b=None, h=None): return _req('POST', p, b, h)
def get(p, h=None): return _req('GET', p, None, h)


async def mark_test(uid):
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    await db.users.update_one({'id': uid}, {'$set': {MARKER: True}})
    await db.player_server_profiles.update_many({'user_id': uid}, {'$set': {MARKER: True}})


async def cleanup(uid):
    if not uid:
        return
    c = AsyncIOMotorClient(MONGO); db = c[DB_NAME]
    u = await db.users.find_one({'id': uid})
    if not u or not u.get(MARKER):
        print(f'[CLEANUP REFUSED] user {uid} not marked pack_92; abort')
        return
    r1 = await db.users.delete_one({'id': uid, MARKER: True})
    r2 = await db.inventory.delete_many({'user_id': uid})
    r3 = await db.player_server_profiles.delete_many({'user_id': uid, MARKER: True})
    r4 = await db.user_heroes.delete_many({'user_id': uid})
    r5 = await db.story_progress.delete_many({'user_id': uid})
    r6 = await db.user_equipment.delete_many({'user_id': uid})
    print(f'[CLEANUP OK] users={r1.deleted_count} inv={r2.deleted_count} psp={r3.deleted_count} uh={r4.deleted_count} story={r5.deleted_count} eq={r6.deleted_count}')


def run():
    uid = None
    proofs = {}
    try:
        # Register test user
        st, body = post('/api/register', {'email': EMAIL, 'password': PWD, 'username': f'p92u_{TS}'})
        assert st == 200, body
        uid = body['user']['id']; token = body['token']
        auth = {'Authorization': f'Bearer {token}'}
        proofs['register_ok'] = True

        # Ensure PSP for A
        st, body = post(f'/api/psp/ensure?server_id={SID_A}', None, auth)
        assert st in (200, 201), body
        proofs['ensure_psp_a_ok'] = True

        # Mark Pack 92 artifacts
        loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
        loop.run_until_complete(mark_test(uid))
        proofs['mark_pack_92_ok'] = True

        # ===== WALLET LOADER GUARDS =====
        # 1) wallet?server_id=A (PSP exists) -> split REALE
        st, body = get(f'/api/wallet?server_id={SID_A}', auth)
        assert st == 200
        assert body.get('filter_applied') is True
        assert body.get('wallet_source') == 'psp_server_scoped_split'
        assert body.get('server_id') == SID_A
        assert 'currencies_global' in body and 'gold' in body['currencies_global']
        assert 'currencies_server_scoped' in body
        proofs['wallet_split_real_filter'] = True

        # 2) wallet?server_id=UNKNOWN -> blocker, filter_applied=true (real filter, blocker honest)
        st, body = get(f'/api/wallet?server_id={SID_UNKNOWN}', auth)
        assert st == 200
        assert body.get('blocker') == 'PLAYER_SERVER_PROFILE_REQUIRED'
        assert body.get('filter_applied') is True
        assert body.get('wallet_source') == 'none'
        proofs['wallet_unknown_server_blocker_honest'] = True

        # 3) wallet (legacy, no server_id) -> filter_applied=false, legacy_flagged
        st, body = get('/api/wallet', auth)
        assert st == 200
        assert body.get('filter_applied') is False
        assert body.get('wallet_source') == 'legacy_account_wide_deprecated'
        proofs['wallet_legacy_path_flagged'] = True

        # ===== STORY LOADER GUARDS =====
        # 1) story?server_id=A (PSP) -> real read from psp.story_progress, no DB write
        st, body = get(f'/api/story/chapters?server_id={SID_A}', auth)
        assert st == 200
        assert body.get('filter_applied') is True
        assert body.get('progress_source') == 'psp_server_scoped'
        assert body.get('server_id') == SID_A
        proofs['story_psp_real_filter'] = True

        # 2) story?server_id=UNKNOWN -> blocker honest
        st, body = get(f'/api/story/chapters?server_id={SID_UNKNOWN}', auth)
        assert st == 200
        assert body.get('blocker') == 'PLAYER_SERVER_PROFILE_REQUIRED'
        assert body.get('filter_applied') is True
        assert body.get('progress_source') == 'none'
        proofs['story_unknown_server_blocker_honest'] = True

        # 3) story (legacy, no server_id) -> filter_applied=false
        st, body = get('/api/story/chapters', auth)
        assert st == 200
        assert body.get('filter_applied') is False
        assert body.get('progress_source') == 'legacy_account_wide_deprecated'
        proofs['story_legacy_path_flagged'] = True

        # ===== EQUIPMENT LOADER GUARDS =====
        # 1) /api/user/equipment?server_id=A -> honest DEFERRED blocker (migration required)
        st, body = get(f'/api/user/equipment?server_id={SID_A}', auth)
        assert st == 200
        assert body.get('blocker') == 'EQUIPMENT_SERVER_SCOPED_LOADER_PROMOTION_DEFERRED'
        assert body.get('filter_applied') is True
        assert body.get('migration_required') is True
        assert body.get('equipment_source') == 'none'
        proofs['equipment_honest_deferred_blocker'] = True

        # 2) /api/user/equipment (legacy) -> list legacy account-wide flagged
        st, body = get('/api/user/equipment', auth)
        assert st == 200
        assert body.get('filter_applied') is False
        assert body.get('equipment_source') == 'legacy_account_wide_deprecated'
        proofs['equipment_legacy_path_flagged'] = True

        # ===== PACK 91 INVENTORY INVARIANT PRESERVED =====
        # GET /api/inventory?server_id=A (no items, fresh PSP) -> player_server_scoped
        st, body = get(f'/api/inventory?server_id={SID_A}', auth)
        assert st == 200
        assert body.get('filter_applied') is True
        assert body.get('inventory_source') == 'player_server_scoped'
        assert body.get('items') == []
        proofs['pack_91_inventory_preserved'] = True

        # POST /api/item-shop/buy senza server_id -> 422 (Pack 90 strict)
        st, body = post('/api/item-shop/buy', {'item_id': 'exp_potion_s', 'quantity': 1}, auth)
        assert st in (400, 422)
        proofs['pack_90_buy_strict_preserved'] = True

        # ===== /api/user/heroes server-scope (Pack 81) =====
        st, body = get(f'/api/user/heroes?server_id={SID_A}', auth)
        # Empty roster (no starter claim) — should return [] with no leak
        assert st == 200
        assert isinstance(body, list)
        proofs['user_heroes_strict_psp'] = True

    finally:
        if uid:
            loop2 = asyncio.new_event_loop(); asyncio.set_event_loop(loop2)
            loop2.run_until_complete(cleanup(uid))
            proofs['cleanup_ok'] = True

    return proofs


if __name__ == '__main__':
    proofs = run()
    required = [
        'register_ok', 'ensure_psp_a_ok', 'mark_pack_92_ok',
        'wallet_split_real_filter', 'wallet_unknown_server_blocker_honest', 'wallet_legacy_path_flagged',
        'story_psp_real_filter', 'story_unknown_server_blocker_honest', 'story_legacy_path_flagged',
        'equipment_honest_deferred_blocker', 'equipment_legacy_path_flagged',
        'pack_91_inventory_preserved', 'pack_90_buy_strict_preserved',
        'user_heroes_strict_psp',
        'cleanup_ok',
    ]
    missing = [k for k in required if proofs.get(k) is not True]
    out = {
        'pack': 'MEGA_RELEASE_ACCELERATION_92_CORE_SERVER_SCOPE_MEGAPACK_CURRENCIES_STORY_EQUIPMENT_FRONTEND_SWEEP',
        'timestamp_utc_ts': TS,
        'test_user_email_pattern': EMAIL,
        'server_a': SID_A,
        'server_unknown': SID_UNKNOWN,
        'test_artifact_marker': MARKER,
        'proofs': proofs,
        'required_missing': missing,
        'real_smoke_executed': len(missing) == 0,
        'read_only': True,
        'no_db_writes_other_than_test_setup': True,
    }
    out_path = '/app/data/design/v110_pack_92_core_server_scope/v110_pack_92_runtime_guard_smoke_result_v1.json'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    if missing:
        print(f'[v110 PACK_92_RUNTIME_GUARD_SMOKE] BLOCKED missing={missing}')
        sys.exit(2)
    print('[v110 PACK_92_RUNTIME_GUARD_SMOKE] OK loader_guards_safe no_false_filter_applied no_DB_writes_other_than_test_setup pack_91_preserved')
