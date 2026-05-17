#!/usr/bin/env python3
"""AF2-N controlled runtime flip canary smoke + monitoring validator.

Reads the live canary-status endpoint and the ledger to verify all V12
acceptance gates. NO DB writes performed by this script.

Gates:
  - runtime flag ON (canary)
  - allowlist size >= 1
  - cap > 0 and ledger total < cap
  - Borea aliases 404 (3 paths)
  - non-allowlist user 423
  - allowlist user canary spend returns 200 with applied_canary (idempotent_replay path also OK)
  - idempotent replay returns 200 with result=idempotent_replay (no new row)
  - ledger inserted rows have canary=true, status=applied_canary, all required safety fields false
  - inventory mutation, affinity points mutation, buffs, battle wiring: NEVER true
  - /api/heroes count == 100, Borea hidden
  - battle_engine.py, battle_core.py, combat.tsx, game_systems.py, synergy_system.py UNCHANGED
"""
from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

API = 'http://127.0.0.1:8001/api'
failures: list[str] = []
checks: list[tuple[str,bool,str]] = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

def _get(p):
    try:
        with urlopen(API+p, timeout=6) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e: return e.code, None
    except URLError: return -1, None

def _post(p, b):
    req = Request(API+p, data=json.dumps(b).encode(), method='POST', headers={'Content-Type':'application/json'})
    try:
        with urlopen(req, timeout=6) as r: return r.status, json.loads(r.read().decode())
    except HTTPError as e:
        try: return e.code, json.loads(e.read().decode())
        except: return e.code, None
    except URLError: return -1, None

code, status = _get('/affinity/gift-spend/canary-status')
rec('status_endpoint_200', code == 200, f'got {code}')
if isinstance(status, dict):
    rec('status_runtime_on', status.get('runtime_attached') is True, '')
    rec('status_feature_flag_on', status.get('feature_flag_currently_enabled') is True, '')
    rec('status_allowlist_size_min_1', status.get('canary_allowlist_size', 0) >= 1, '')
    rec('status_cap_positive', status.get('canary_ledger_cap', 0) > 0, '')
    rec('status_ledger_below_cap',
        status.get('ledger_total_rows', 99999) < status.get('canary_ledger_cap', 0), '')
    rec('status_canary_only_writes',
        status.get('ledger_total_rows') == status.get('ledger_canary_rows'), '')
    rec('status_combat_off', status.get('applied_to_combat') is False, '')
    rec('status_battle_off', status.get('battle_runtime_attached') is False, '')
    rec('status_inventory_off', status.get('inventory_mutation_enabled') is False, '')
    rec('status_affinity_points_off', status.get('affinity_points_mutation_enabled') is False, '')
    rec('status_buffs_off', status.get('buffs_enabled') is False, '')
    rec('status_borea_blocked', status.get('borea_aliases_blocked') == ['borea','greek_borea','primordial_gaia'], '')

# Borea always 404
for hid in ('borea', 'greek_borea', 'primordial_gaia'):
    code, _ = _post('/affinity/gift-spend',
        {'gift_id':'x','hero_id':hid,'quantity':1,'idempotency_key':'abcd1234efgh','user_id':'user_canary_001'})
    rec(f'live_{hid}_404', code == 404, f'got {code}')

# Non-allowlist user blocked
code, _ = _post('/affinity/gift-spend',
    {'gift_id':'gift_x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'randomidem9999','user_id':'unauth_user_xxx'})
rec('live_non_allowlist_423', code == 423, f'got {code}')

# Allowlist user idempotent replay: must return 200 with no new row
before = status.get('ledger_total_rows') if isinstance(status, dict) else None
code, body = _post('/affinity/gift-spend',
    {'gift_id':'gift_test_001','hero_id':'greek_zeus','quantity':1,
     'idempotency_key':'canary_idem_0001','user_id':'user_canary_001'})
rec('live_idem_replay_200', code == 200, f'got {code}')
if isinstance(body, dict):
    rec('live_idem_replay_no_new_row', body.get('ledger_row_inserted') is False, '')
    rec('live_idem_replay_result', body.get('result') == 'idempotent_replay', '')
code, status2 = _get('/affinity/gift-spend/canary-status')
if isinstance(status2, dict) and before is not None:
    rec('live_ledger_unchanged_after_idem_replay',
        status2.get('ledger_total_rows') == before, f'before={before} after={status2.get("ledger_total_rows")}')

# /api/heroes count + Borea hidden
code, data = _get('/heroes')
rec('live_heroes_reachable', code in (200, 304), f'got {code}')
if isinstance(data, list):
    rec('live_heroes_count_100', len(data) == 100, f'got {len(data)}')
    ids = {h.get('id') for h in data if isinstance(h, dict)}
    rec('live_borea_hidden', not (ids & {'borea','greek_borea','primordial_gaia'}), '')

# Battle files unchanged (git diff)
try:
    out = subprocess.run(
        ['git', '-C', '/app', 'diff', '--stat', '--',
         'backend/battle_engine.py', 'backend/battle_core.py',
         'frontend/app/combat.tsx', 'backend/game_systems.py',
         'backend/synergy_system.py'],
        capture_output=True, text=True, timeout=10)
    rec('battle_files_unchanged', out.stdout.strip() == '', f'diff={out.stdout!r}')
except Exception as e:
    rec('battle_files_unchanged', False, f'{e!r}')

# Ledger row sanity
try:
    from pymongo import MongoClient
    coll = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']['gift_transaction_ledger']
    total = coll.count_documents({})
    canary_only = coll.count_documents({'canary': True})
    rec('ledger_only_canary_writes', total == canary_only, f'total={total} canary={canary_only}')
    bad_inventory = coll.count_documents({'inventory_mutated': True})
    bad_points = coll.count_documents({'affinity_points_mutated': True})
    bad_buffs = coll.count_documents({'buffs_activated': True})
    bad_battle = coll.count_documents({'battle_wiring_attached': True})
    rec('ledger_no_inventory_mutation_anywhere', bad_inventory == 0, f'got {bad_inventory}')
    rec('ledger_no_affinity_points_mutation', bad_points == 0, f'got {bad_points}')
    rec('ledger_no_buffs_activated', bad_buffs == 0, f'got {bad_buffs}')
    rec('ledger_no_battle_wiring', bad_battle == 0, f'got {bad_battle}')
    # Borea must NEVER appear as hero_id in ledger
    borea_count = coll.count_documents({'hero_id': {'$in': ['borea','greek_borea','primordial_gaia']}})
    rec('ledger_no_borea_hero', borea_count == 0, f'got {borea_count}')
    # All canary writes have status applied_canary
    bad_status = coll.count_documents({'canary': True, 'status': {'$ne': 'applied_canary'}})
    rec('ledger_all_canary_status_applied_canary', bad_status == 0, '')
except Exception as e:
    rec('ledger_only_canary_writes', False, f'{e!r}')

print('='*70); print('AF2-N CANARY SMOKE + MONITORING — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
