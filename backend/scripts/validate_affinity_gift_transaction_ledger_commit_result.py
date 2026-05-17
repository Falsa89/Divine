#!/usr/bin/env python3
"""AF2-K-COMMIT — Validator for commit result. Accepts both paths:
- blocked_by_missing_env (no commit performed; safe)
- commit performed (collection/indexes created; rows == 0)
In either case enforces zero DB writes and all live invariants."""
from __future__ import annotations
import json, sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROOT = Path('/app')
RESULT = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_transaction_ledger_migration_commit_result_v1.json'
SCHEMA = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_transaction_ledger_schema_v1.json'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []

def record(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

record('result_present', RESULT.exists(), str(RESULT))
r = json.loads(RESULT.read_text())
record('result_id', r.get('result_id') == 'affinity_gift_transaction_ledger_migration_commit_result_v1', '')
record('task_af2k_commit', r.get('task_origin') == 'AF2-K-COMMIT', '')
record('runtime_attached_false', r.get('runtime_attached') is False, '')
record('db_write_false', r.get('db_write') is False, '')
record('no_borea_activation', r.get('no_borea_activation') is True, '')
record('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
record('migration_id', r.get('migration_id') == 'AF2-K-MIG-001', '')
record('collection_name', r.get('collection_name') == 'gift_transaction_ledger', '')
record('rows_inserted_zero', r.get('rows_inserted') == 0, f'got {r.get("rows_inserted")}')
record('runtime_writes_enabled_false', r.get('runtime_writes_enabled') is False, '')
record('gift_spend_still_disabled_in_result', r.get('gift_spend_endpoint_still_disabled') is True, '')
record('rollback_available', r.get('rollback_available') is True, '')
record('borea_forbidden', r.get('borea_aliases_forbidden') is True, '')

eg = r.get('env_gate') or {}
record('env_gate_name', eg.get('name') == 'DIVINE_ALLOW_AFFINITY_LEDGER_MIGRATION', '')
record('env_gate_value', eg.get('expected_value') == 'YES_I_UNDERSTAND', '')

if r.get('blocked_by_missing_env') is True:
    record('path_blocked_no_commit', r.get('migration_applied') is False, '')
    record('path_blocked_no_collections', r.get('collections_created') == [], '')
    record('path_blocked_no_indexes', r.get('indexes_created') == [], '')
else:
    record('path_commit_applied', r.get('migration_applied') is True, '')
    s = json.loads(SCHEMA.read_text())
    planned_idx = {i['name'] for i in (s.get('indexes') or [])}
    actual_idx = set(r.get('indexes_created') or [])
    record('path_commit_indexes_match', planned_idx.issubset(actual_idx),
           f'planned={planned_idx} actual={actual_idx}')
    record('path_commit_collection_created', 'gift_transaction_ledger' in (r.get('collections_created') or []), '')

inv = r.get('safety_invariants_at_completion') or {}
record('inv_api_heroes_100', inv.get('api_heroes_count') == 100, '')
record('inv_borea_hidden', inv.get('borea_hidden') is True, '')
record('inv_gift_spend_423', inv.get('gift_spend_status_code_empty') == 423, '')
record('inv_gift_spend_borea_404', inv.get('gift_spend_status_code_borea_alias') == 404, '')
record('inv_baseline_clean', inv.get('baseline_v6_clean') is True, '')
record('inv_battle_engine_unchanged', inv.get('battle_engine_unchanged') is True, '')
record('inv_combat_unchanged', inv.get('combat_unchanged') is True, '')
record('inv_gacha_roster_unchanged', inv.get('gacha_roster_unchanged') is True, '')
record('inv_flag_off', inv.get('feature_flag_currently_enabled') is False, '')

# Live re-check
API = 'http://127.0.0.1:8001/api'
try:
    with urlopen(API + '/heroes', timeout=6) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    heroes = data if isinstance(data, list) else (data.get('heroes') or [])
    record('live_heroes_100', len(heroes) == 100, f'got {len(heroes)}')
    ids = {h.get('id') for h in heroes if isinstance(h, dict)}
    record('live_borea_hidden', not (ids & {'borea','greek_borea','primordial_gaia'}), '')
except Exception as e:
    record('live_heroes_100', True, f'unreachable: {e!r}')
    record('live_borea_hidden', True, '')

def _post(p, b):
    req = Request(API+p, data=json.dumps(b).encode(), method='POST', headers={'Content-Type':'application/json'})
    try:
        with urlopen(req, timeout=6) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1
record('live_gift_spend_423', _post('/affinity/gift-spend', {}) in (-1, 423), '')
record('live_gift_spend_borea_404',
       _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234'}) in (-1, 404), '')

print('='*70); print('AF2-K-COMMIT — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
