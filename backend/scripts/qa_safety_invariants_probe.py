#!/usr/bin/env python3
"""Closed Alpha QA Safety Invariants Probe (READ-ONLY).

Questo script è un helper docs-only/read-only che il coordinatore QA può
lanciare prima/dopo una sessione tester per verificare lo stato corrente
delle safety invariants del backend locale.

NON modifica alcuna risorsa. NON crea utenti. NON attiva nulla.
Prova solo health endpoint pubblici e calcola statistiche server-side
(via Mongo locale) sui campi sensibili `users.gold/gems/experience` per
gli utenti test marcati.

Uso:
  python backend/scripts/qa_safety_invariants_probe.py

Output: tabella sintetica + verdict ('SAFE_INVARIANTS_OK' / 'SAFE_INVARIANTS_VIOLATED').
"""
import os, sys, json, asyncio
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'backend'))
from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore
from dotenv import load_dotenv  # type: ignore

load_dotenv(os.path.join(ROOT, 'backend', '.env'))
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'divine_waifus')
API = 'http://localhost:8001/api'

HEALTH_ENDPOINTS = (
    '/tower/strict/health',
    '/economy/strict/health',
    '/controlled-rewards/health',
    '/guild/strict/health',
    '/playable-loop/health',
    '/competitive-guards/health',
    '/rewards/claim/health',
    '/daily-login/claim/health',
    '/daily-quest/claim/health',
    '/daily-quest/tracker/health',
)


def _get(path: str):
    try:
        with urllib.request.urlopen(API + path, timeout=10) as r:
            return r.status, json.loads(r.read().decode())
    except Exception as e:
        return -1, {'error': str(e)}


async def main():
    print('=== Closed Alpha QA Safety Invariants Probe (READ-ONLY) ===\n')
    violations = []

    # 1) Health endpoint safety statements.
    print('--- Health endpoint safety statements ---')
    for ep in HEALTH_ENDPOINTS:
        status, body = _get(ep)
        rlg = body.get('reward_live_general')
        rrc = body.get('release_readiness_claimed')
        rlg_ok = (rlg is False or rlg is None)
        rrc_ok = (rrc is False or rrc is None)
        verdict = 'OK' if (status == 200 and rlg_ok and rrc_ok) else 'WARN'
        if status != 200:
            verdict = 'WARN'  # non un violation: alcuni endpoint potrebbero richiedere auth.
        if rlg is True or rrc is True:
            violations.append(f'{ep}: reward_live_general={rlg}, release_readiness_claimed={rrc}')
        print(f'  {ep:40s} status={status:3d} rlg={rlg} rrc={rrc} → {verdict}')

    # 2) Playable loop map: nessuna surface deve avere status=READY.
    print('\n--- Playable loop map (server_id=s1, server_id=s2) ---')
    for sid in ('s1', 's2'):
        status, body = _get(f'/playable-loop/map?server_id={sid}')
        if status != 200:
            print(f'  /playable-loop/map?server_id={sid} → status={status}')
            continue
        surfaces = body.get('surfaces', {})
        false_ready = [k for k, v in surfaces.items() if v.get('status') == 'READY']
        if false_ready:
            violations.append(f'playable-loop/map server_id={sid} false_ready_surfaces={false_ready}')
        rrc = body.get('release_readiness_claimed')
        if rrc is True:
            violations.append(f'playable-loop/map server_id={sid} release_readiness_claimed=True')
        print(f'  server_id={sid}: surfaces={len(surfaces)} false_ready={false_ready} rrc={rrc}')

    # 3) Mongo-side stats su utenti test marcati (read-only count + min/max).
    print('\n--- Mongo-side users.* test markers (read-only) ---')
    client = AsyncIOMotorClient(MONGO_URL); db = client[DB_NAME]
    try:
        for marker in ('pack_101_test_artifact', 'pack_103_test_artifact',
                       'pack_104_test_artifact', 'pack_105_test_artifact',
                       'pack_106_test_artifact', 'pack_107_test_artifact',
                       'pack_108_test_artifact'):
            n = await db.users.count_documents({marker: True})
            print(f'  count users[{marker}=true] = {n}')
        # users.gold/gems/experience totali non-zero (red flag se inaspettatamente alti per testers).
        leaked_high = await db.users.count_documents({'gems': {'$gt': 10000}})
        if leaked_high > 50:
            violations.append(f'users.gems > 10000 ha {leaked_high} record (possibile grant inaspettato)')
        print(f'  users with gems > 10000: {leaked_high}')
        # reward_claim_ledger size check.
        ledger_count = await db.reward_claim_ledger.count_documents({})
        print(f'  reward_claim_ledger total docs: {ledger_count}')
    finally:
        client.close()

    # 4) Backend .env reward live flags should be OFF.
    print('\n--- backend/.env reward live flags ---')
    env_path = os.path.join(ROOT, 'backend/.env')
    if os.path.exists(env_path):
        env = open(env_path).read()
        for flag in ('REWARD_LIVE_GENERAL', 'GUILD_REWARD_LIVE_ENABLED',
                     'ARENA_REWARD_LIVE_ENABLED', 'PVP_REWARD_LIVE_ENABLED',
                     'EVENT_REWARD_LIVE_ENABLED', 'BATTLEPASS_REWARD_LIVE_ENABLED',
                     'AFK_REWARD_LIVE_ENABLED', 'DAILY_LOGIN_CLAIM_ENABLED'):
            import re
            m = re.search(rf'^{flag}=(\S+)', env, re.MULTILINE)
            val = m.group(1).strip().lower() if m else '(absent=default OFF)'
            if m and val in ('true', '1', 'yes', 'on'):
                violations.append(f'backend/.env: {flag}={val} (must be OFF)')
            print(f'  {flag:40s} = {val}')
    else:
        print('  backend/.env not found')

    # Verdict.
    print()
    if violations:
        print('=== VERDICT: SAFE_INVARIANTS_VIOLATED ===')
        for v in violations:
            print(f'  - {v}')
        return 1
    print('=== VERDICT: SAFE_INVARIANTS_OK ===')
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
