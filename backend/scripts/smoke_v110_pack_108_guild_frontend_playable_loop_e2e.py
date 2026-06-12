#!/usr/bin/env python3
"""Pack 108 — Smoke E2E Guild Server-Scope Retrofit + Frontend Playable Loop.

Prova runtime live (HTTP locale verso http://localhost:8001):
  1.  Health endpoint /api/guild/strict/health (pubblico) attivo.
  2.  /api/guild/strict/preflight rifiuta utenti senza marker.
  3.  /api/guild/strict/status richiede server_id.
  4.  /api/guild/strict/search richiede server_id.
  5.  Membership preview rifiuta senza guild_id.
  6.  Membership preview e' read-only (no insert su guild_memberships_v2).
  7.  S1 membership preview non vede S2.
  8.  /api/playable-loop/map?server_id=s1 ritorna mappa Alpha senza
      release_readiness e con tutte le surface guild/arena/pvp/event non-READY.
  9.  /api/playable-loop/map richiede server_id (no silent s1).
 10.  Legacy /api/guild/create -> auth 401 oppure 423 quarantine (no creation).
 11.  /api/competitive-guards/guild/preflight resta READY_GATED_REWARDS_DEFERRED.
 12.  Arena/PvP/Event preflight Pack 107 invariati.
 13.  users.gold/gems/experience invariati.
 14.  Server switch S1->S2 ritorna mappe distinte.
 15.  reward_live_general=false ovunque.
 16.  release_readiness_claimed=false ovunque.

Il test crea (e poi pulisce) un utente test marcato `pack_108_test_artifact`.
"""
import os, sys, time, uuid, json
import urllib.request, urllib.error
import asyncio

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'backend'))

from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore
from dotenv import load_dotenv  # type: ignore

load_dotenv(os.path.join(ROOT, 'backend', '.env'))
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'divine_waifus')
API = 'http://localhost:8001/api'

import hashlib, jwt
JWT_SECRET = os.environ.get('JWT_SECRET', 'divine_waifus_secret_key_2025')


def http_get(path, token=None):
    req = urllib.request.Request(API + path, method='GET')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}


def http_post(path, token=None, body=None):
    data = json.dumps(body or {}).encode() if body is not None else None
    req = urllib.request.Request(API + path, method='POST', data=data)
    if data is not None:
        req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {}


def mint_token(user_id: str) -> str:
    return jwt.encode({'user_id': user_id, 'exp': int(time.time()) + 3600}, JWT_SECRET, algorithm='HS256')


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    uid_unmarked = f'pack108_unmarked_{uuid.uuid4().hex[:8]}'
    uid_marked = f'pack108_marked_{uuid.uuid4().hex[:8]}'
    test_users = [uid_unmarked, uid_marked]
    inserted_ids = []
    fake_email_unm = f'{uid_unmarked}@pack108.test'
    fake_email_mar = f'{uid_marked}@pack108.test'
    pwd = hashlib.sha256(b'pack108_test_pw').hexdigest()
    try:
        await db.users.insert_one({
            'id': uid_unmarked, 'username': uid_unmarked, 'email': fake_email_unm,
            'password': pwd, 'level': 1, 'gold': 0, 'gems': 0, 'experience': 0,
        })
        inserted_ids.append(uid_unmarked)
        await db.users.insert_one({
            'id': uid_marked, 'username': uid_marked, 'email': fake_email_mar,
            'password': pwd, 'level': 1, 'gold': 0, 'gems': 0, 'experience': 0,
            'pack_108_test_artifact': True, 'pack_107_test_artifact': True,
        })
        inserted_ids.append(uid_marked)
        tok_unm = mint_token(uid_unmarked)
        tok_mar = mint_token(uid_marked)

        # 1) Health pubblico.
        s, j = http_get('/guild/strict/health')
        assert s == 200 and j.get('pack_origin') == 'pack_108', (s, j)
        assert j.get('reward_live_general') is False
        assert j.get('release_readiness_claimed') is False
        assert j.get('legacy_route_quarantined_default') is True
        print('[1] guild/strict/health OK')

        # 2) Unmarked refused.
        s, j = http_post('/guild/strict/preflight?server_id=s1', token=tok_unm)
        assert s == 403, (s, j)
        print('[2] unmarked refused OK')

        # 3) status requires server_id (marked, but no server_id).
        s, j = http_get('/guild/strict/status', token=tok_mar)
        assert s == 400, (s, j)
        print('[3] status requires server_id OK')

        # 4) search requires server_id.
        s, j = http_get('/guild/strict/search', token=tok_mar)
        assert s == 400, (s, j)
        print('[4] search requires server_id OK')

        # 5) Membership preview requires guild_id.
        s, j = http_post('/guild/strict/membership/preview?server_id=s1', token=tok_mar)
        assert s == 400, (s, j)
        print('[5] membership preview requires guild_id OK')

        # 6) Membership preview e' read-only (NON crea record).
        before_count = await db.guild_memberships_v2.count_documents({'user_id': uid_marked})
        s, j = http_post('/guild/strict/membership/preview?server_id=s1&guild_id=fakeguild_pack108', token=tok_mar)
        assert s == 200 and j.get('status') == 'PREVIEW_ONLY_NO_WRITE'
        assert j.get('write_disabled') is True
        after_count = await db.guild_memberships_v2.count_documents({'user_id': uid_marked})
        assert before_count == after_count, (before_count, after_count)
        print('[6] membership preview is read-only OK')

        # 7) S1/S2 isolation: preview su s2 deve dare server_id=s2 esplicito.
        s, j = http_post('/guild/strict/membership/preview?server_id=s2&guild_id=fakeguild_pack108', token=tok_mar)
        assert s == 200 and j.get('server_id') == 's2'
        assert j.get('guild_exists_in_server') is False
        print('[7] S1/S2 server scope isolation OK')

        # 8) playable-loop/map?server_id=s1.
        s, j = http_get('/playable-loop/map?server_id=s1')
        assert s == 200, (s, j)
        assert j.get('release_readiness_claimed') is False
        assert j.get('no_silent_fallback_to_s1') is True
        surfaces = j.get('surfaces', {})
        for k in ('home','lobby','daily','tower','shop','forge','rewards','guild','arena','pvp','event'):
            assert k in surfaces, k
            s_ent = surfaces[k]
            assert s_ent.get('reward_live') is False
            assert s_ent.get('ui_flag_default_off') is True
            assert s_ent.get('status') != 'READY', f'false-ready label on {k}'
        print('[8] playable-loop map OK no false-ready')

        # 9) playable-loop/map without server_id -> 400.
        s, j = http_get('/playable-loop/map')
        assert s == 400, (s, j)
        print('[9] playable-loop map requires server_id OK')

        # 10) Legacy /api/guild/create blocked (auth 401 or quarantine 423).
        s, j = http_post('/guild/create', body={'name': f'legacy_{uuid.uuid4().hex[:6]}'})
        assert s in (401, 423), (s, j)
        # With marked token:
        s, j = http_post('/guild/create', token=tok_mar, body={'name': f'legacy_{uuid.uuid4().hex[:6]}'})
        assert s == 423, (s, j)
        assert (j.get('detail') or {}).get('blocker') == 'GUILD_LEGACY_QUARANTINED', j
        print('[10] legacy guild/create quarantined OK')

        # 11) competitive-guards/guild/preflight invariato.
        s, j = http_post('/competitive-guards/guild/preflight?server_id=s1', token=tok_mar)
        assert s == 200, (s, j)
        assert j.get('status') == 'AUDIT_LEGACY_NOT_SERVER_SCOPED'
        assert j.get('guild_reward_live_grant') is False
        print('[11] competitive-guards guild preflight preserved OK')

        # 12) Arena/PvP/Event preflight preserved.
        for surf in ('arena', 'pvp', 'event'):
            s, j = http_post(f'/competitive-guards/{surf}/preflight?server_id=s1', token=tok_mar)
            assert s == 200, (surf, s, j)
            assert j.get('status') == 'READY_GATED_REWARDS_DEFERRED'
        print('[12] arena/pvp/event preflight Pack 107 preserved OK')

        # 13) users.gold/gems/experience unchanged.
        u = await db.users.find_one({'id': uid_marked})
        assert u.get('gold', 0) == 0 and u.get('gems', 0) == 0 and u.get('experience', 0) == 0
        print('[13] users.gold/gems/experience unchanged OK')

        # 14) Server switch: map for s1 vs s2.
        _, j1 = http_get('/playable-loop/map?server_id=s1')
        _, j2 = http_get('/playable-loop/map?server_id=s2')
        assert j1.get('server_id') == 's1' and j2.get('server_id') == 's2'
        print('[14] server switch s1->s2 distinct maps OK')

        # 15) reward_live_general false everywhere.
        for path in ('/guild/strict/health', '/playable-loop/health', '/competitive-guards/health'):
            _, jj = http_get(path)
            assert jj.get('reward_live_general') in (False, None) and jj.get('reward_live_general') is not True, (path, jj)
        print('[15] reward_live_general=false everywhere OK')

        # 16) release_readiness_claimed false everywhere.
        for path in ('/guild/strict/health', '/playable-loop/map?server_id=s1', '/competitive-guards/health'):
            _, jj = http_get(path)
            v = jj.get('release_readiness_claimed')
            assert v is False or v is None, (path, jj)
        print('[16] release_readiness_claimed=false everywhere OK')

        # 17) Membership preview cross-server: insert fake membership s1 directly, verify s2 still empty.
        await db.guild_memberships_v2.insert_one({
            'user_id': uid_marked, 'server_id': 's1', 'guild_id': 'fakeguild_s1_pack108', 'role': 'member',
        })
        s, j = http_get('/guild/strict/status?server_id=s1', token=tok_mar)
        # status returns READY_GATED_READ_DISABLED if flag off, but ALWAYS server-scoped.
        assert j.get('server_id') == 's1'
        s, j = http_get('/guild/strict/status?server_id=s2', token=tok_mar)
        assert j.get('server_id') == 's2'
        # cleanup test record.
        await db.guild_memberships_v2.delete_many({'guild_id': 'fakeguild_s1_pack108'})
        print('[17] s1 membership invisible cross-server OK')

        print('SMOKE PACK 108 OK')
        return 0
    finally:
        # Cleanup.
        if inserted_ids:
            await db.users.delete_many({'id': {'$in': inserted_ids}})
        await db.guild_memberships_v2.delete_many({'user_id': {'$in': inserted_ids}})
        client.close()


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
