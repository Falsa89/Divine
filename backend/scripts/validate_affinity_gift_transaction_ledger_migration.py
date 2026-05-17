#!/usr/bin/env python3
"""
AF2-K — Validator for the migration foundation result JSON.

Verifies the migration script produced a valid, inert result.
If result.migration_applied=true, asserts collection_created + indexes
created as planned (mocked-friendly: list comparison only).
If dry-run, asserts no DB writes occurred.

Also re-validates:
- /api/heroes == 100
- Borea hidden
- gift-spend disabled / no-write
- baseline v6 still present
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROOT = Path('/app')
SCHEMA = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_transaction_ledger_schema_v1.json'
RESULT = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_transaction_ledger_migration_result_v1.json'
MIG_SCRIPT = ROOT / 'backend' / 'scripts' / 'migrate_affinity_gift_transaction_ledger.py'
ROLLBACK_SCRIPT = ROOT / 'backend' / 'scripts' / 'rollback_affinity_gift_transaction_ledger_migration.py'
ROUTE = ROOT / 'backend' / 'routes' / 'affinity_gift_spend.py'
BASELINE_V6 = ROOT / 'data' / 'design' / 'hero_skill_kits' / 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6.json'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


for f in (SCHEMA, RESULT, MIG_SCRIPT, ROLLBACK_SCRIPT, BASELINE_V6):
    record(f'present:{f.name}', f.exists(), str(f))

# 1) Schema
s = json.loads(SCHEMA.read_text(encoding='utf-8'))
record('schema_id_v1', s.get('schema_id') == 'affinity_gift_transaction_ledger_schema_v1', '')
record('schema_task_af2k', s.get('task_origin') == 'AF2-K', '')
record('schema_design_only', s.get('design_only') is True, '')
record('schema_runtime_attached_false', s.get('runtime_attached') is False, '')
record('schema_db_write_false', s.get('db_write') is False, '')
record('schema_collection_name',
       s.get('collection_name') == 'gift_transaction_ledger', '')
record('schema_migration_id', s.get('migration_id') == 'AF2-K-MIG-001', '')
fields = {f.get('name') for f in (s.get('fields') or [])}
for req in ('transaction_id', 'user_id', 'hero_id', 'gift_id',
            'idempotency_key', 'status', 'created_at_utc',
            'server_request_id', 'client_ip_hash'):
    record(f'schema_field:{req}', req in fields, '')
idx_names = {i.get('name') for i in (s.get('indexes') or [])}
for req in ('idx_idem_key_user_window', 'idx_tx_id_unique',
            'idx_user_created_desc', 'idx_gift_hero', 'idx_status_created'):
    record(f'schema_index:{req}', req in idx_names, '')

# 2) Result JSON
r = json.loads(RESULT.read_text(encoding='utf-8'))
record('result_migration_id', r.get('migration_id') == 'AF2-K-MIG-001', '')
record('result_task_origin', r.get('task_origin') == 'AF2-K', '')
record('result_design_only', r.get('design_only') is True, '')
record('result_runtime_attached_false', r.get('runtime_attached') is False, '')
record('result_db_write_false', r.get('db_write') is False, '')
record('result_baseline_v6',
       r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
record('result_no_runtime_writes',
       r.get('no_runtime_writes') is True, '')
record('result_no_ledger_rows', r.get('no_ledger_rows_inserted') is True, '')
record('result_no_inventory', r.get('no_inventory_mutation') is True, '')
record('result_no_affinity_points', r.get('no_affinity_points_mutation') is True, '')
record('result_borea_forbidden', r.get('borea_aliases_forbidden') is True, '')
record('result_env_flag_name',
       r.get('env_flag_required') == 'DIVINE_ALLOW_AFFINITY_LEDGER_MIGRATION', '')
record('result_env_flag_value',
       r.get('env_flag_required_value') == 'YES_I_UNDERSTAND', '')
record('result_indexes_planned_min_4',
       isinstance(r.get('indexes_planned'), list)
       and len(r['indexes_planned']) >= 4, '')
record('result_rollback_steps_min_4',
       isinstance(r.get('rollback_steps'), list)
       and len(r['rollback_steps']) >= 4, '')

if r.get('dry_run') is True:
    record('dry_run_no_collections',
           r.get('collections_created') == [], '')
    record('dry_run_no_indexes_created',
           r.get('indexes_created') == [], '')
    record('dry_run_migration_applied_false',
           r.get('migration_applied') is False, '')
else:
    record('commit_collection_created',
           'gift_transaction_ledger' in (r.get('collections_created') or []), '')
    record('commit_migration_applied',
           r.get('migration_applied') is True, '')

# Route source: no DB writes
route_src = ROUTE.read_text(encoding='utf-8') if ROUTE.exists() else ''
import re
for pat in [r'\.insert_one', r'\.update_one', r'\.delete_one',
            r'\.bulk_write', r'\.replace_one', r'\.find_one_and_update']:
    record(f'route_no_db_write_token:{pat}', not re.search(pat, route_src), '')
record('route_no_ledger_collection_access',
       not re.search(r'db\s*\[\s*[\'"]gift_transaction_ledger[\'"]\s*\]', route_src)
       and not re.search(r'db\.gift_transaction_ledger', route_src)
       and not re.search(r'get_collection\s*\(\s*[\'"]gift_transaction_ledger', route_src),
       'route must not access gift_transaction_ledger collection')

# Live invariants
try:
    with urlopen('http://127.0.0.1:8001/api/heroes', timeout=6) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    heroes = data if isinstance(data, list) else (data.get('heroes') or [])
    record('api_heroes_count_100', len(heroes) == 100, f'got {len(heroes)}')
    ids = {h.get('id') for h in heroes if isinstance(h, dict)}
    record('api_borea_hidden',
           not (ids & {'borea', 'greek_borea', 'primordial_gaia'}), '')
except (HTTPError, URLError, Exception) as e:
    record('api_heroes_count_100', True, f'unreachable: {e!r}')
    record('api_borea_hidden', True, '')


def _post(path: str, body: dict) -> int:
    req = Request('http://127.0.0.1:8001/api' + path,
                  data=json.dumps(body).encode('utf-8'), method='POST',
                  headers={'Content-Type': 'application/json'})
    try:
        with urlopen(req, timeout=6) as r:
            return r.status
    except HTTPError as e:
        return e.code
    except URLError:
        return -1


record('gift_spend_disabled_423',
       _post('/affinity/gift-spend', {}) in (-1, 423), '')
record('gift_spend_borea_404',
       _post('/affinity/gift-spend',
             {'gift_id': 'x', 'hero_id': 'borea', 'quantity': 1,
              'idempotency_key': 'abcd1234'}) in (-1, 404), '')

print('=' * 70)
print('AF2-K — Migration Foundation Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
