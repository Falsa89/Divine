#!/usr/bin/env python3
"""
AF2-K-PRE — Validator for the gift_transaction_ledger contract (design-only).

Verifies the JSON contract:
- design_only=true, db_write=false, migration_created=false,
  runtime_attached=false, no_borea_activation=true;
- baseline anchor v6;
- future_collection_name is gift_transaction_ledger;
- idempotency_scope contains user_id, gift_id, hero_id, idempotency_key;
- idempotency window 24h, key length [8,128];
- ledger record schema includes transaction_id, status, idempotency_key;
- ledger index draft has the partial unique idempotency-window index;
- status enumeration includes pending/committed/rolled_back/duplicate_replay
  /rejected_borea_alias/rejected_validation/rejected_rate_limit/rejected_auth;
- duplicate_replay returns 409 with original payload;
- borea_safety blocks borea/greek_borea/primordial_gaia;
- no_write_until lists at least 3 preconditions;
- abuse_cases list has at least 5 entries;
- no DB collection or migration was created in this task (cross-check: no
  /app/backend/data/migrations/AF2-K-MIG-001* file).

Read-only.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
CONTRACT = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_spend_idempotency_ledger_contract_v1.json'
MIG_DIR = ROOT / 'backend' / 'data' / 'migrations'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


record('contract_present', CONTRACT.exists(), str(CONTRACT))
c = json.loads(CONTRACT.read_text(encoding='utf-8')) if CONTRACT.exists() else {}
record('contract_id_v1',
       c.get('contract_id') == 'affinity_gift_spend_idempotency_ledger_contract_v1', '')
record('contract_task_origin_af2k_pre',
       c.get('task_origin') == 'AF2-K-PRE', '')
record('contract_design_only', c.get('design_only') is True, '')
record('contract_db_write_false', c.get('db_write') is False, '')
record('contract_migration_created_false',
       c.get('migration_created') is False, '')
record('contract_runtime_attached_false',
       c.get('runtime_attached') is False, '')
record('contract_no_borea_activation',
       c.get('no_borea_activation') is True, '')
record('contract_baseline_v6',
       c.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
record('future_collection_name',
       c.get('future_collection_name') == 'gift_transaction_ledger', '')
record('future_migration_id',
       isinstance(c.get('future_migration_id'), str)
       and 'AF2-K' in c.get('future_migration_id', ''), '')

scope = c.get('idempotency_scope') or []
for req in ('user_id', 'gift_id', 'hero_id', 'idempotency_key'):
    record(f'idem_scope:{req}', req in scope, f'scope={scope}')
record('idem_window_24', c.get('idempotency_window_hours') == 24, '')
record('idem_key_min_len_8', c.get('idempotency_key_min_length') == 8, '')
record('idem_key_max_len_128', c.get('idempotency_key_max_length') == 128, '')

schema = c.get('ledger_record_schema_draft') or {}
for req in ('transaction_id', 'user_id', 'hero_id', 'gift_id',
            'idempotency_key', 'status', 'created_at_utc'):
    record(f'schema_field:{req}', req in schema, '')

idx = c.get('ledger_index_draft') or []
record('index_draft_min_3', len(idx) >= 3, f'got {len(idx)}')
# Look for partial unique idempotency-window index
has_partial_unique = any(
    isinstance(i, dict)
    and i.get('unique') is True
    and 'idempotency_key' in str(i.get('keys'))
    and 'partial' in i
    for i in idx
)
record('index_partial_unique_idempotency', has_partial_unique, '')

statuses = {st.get('to') for st in (c.get('status_transitions') or [])
            if isinstance(st, dict)}
for req in ('committed', 'rolled_back', 'duplicate_replay',
            'rejected_borea_alias', 'rejected_validation',
            'rejected_rate_limit', 'rejected_auth'):
    record(f'status_transition:{req}', req in statuses, '')

dr = c.get('duplicate_replay_behavior') or {}
record('duplicate_replay_409', dr.get('http_status') == 409, '')
record('duplicate_replay_no_mutation',
       'no state mutation' in (dr.get('return_payload') or '').lower(), '')

bs = c.get('borea_safety') or {}
record('borea_aliases_forbidden',
       bs.get('borea_aliases_forbidden_in_ledger') is True, '')
for alias in ('borea', 'greek_borea', 'primordial_gaia'):
    record(f'borea_alias_blocked:{alias}',
           alias in (bs.get('hidden_aliases_blocked') or []), '')

record('no_write_until_min_3',
       isinstance(c.get('no_write_until'), list)
       and len(c['no_write_until']) >= 3, '')
record('rollback_plan_min_3',
       isinstance(c.get('rollback_plan'), list)
       and len(c['rollback_plan']) >= 3, '')
record('abuse_cases_min_5',
       isinstance(c.get('abuse_cases'), list)
       and len(c['abuse_cases']) >= 5, '')

sf = c.get('safety_flags') or {}
record('sf_runtime_attached_false', sf.get('runtime_attached') is False, '')
record('sf_db_write_false', sf.get('db_write') is False, '')
record('sf_migration_created_false',
       sf.get('migration_created') is False, '')
record('sf_collection_created_false',
       sf.get('collection_created') is False, '')
record('sf_feature_flag_off',
       sf.get('feature_flag_currently_enabled') is False, '')

# No migration file actually shipped
if MIG_DIR.exists():
    mig_files = [p for p in MIG_DIR.glob('AF2-K-MIG-001*')]
    record('no_migration_file_shipped', not mig_files,
           f'unexpected mig files: {mig_files}')
else:
    record('no_migration_file_shipped', True, 'mig dir absent')


print('=' * 70)
print('AF2-K-PRE — Idempotency Ledger Contract Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
