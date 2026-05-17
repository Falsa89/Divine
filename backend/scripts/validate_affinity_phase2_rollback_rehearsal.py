#!/usr/bin/env python3
"""
AF2-F — Validator for the rollback rehearsal result.

1. Executes the rehearsal in dry-run mode (if result missing or stale).
2. Asserts:
   - result file exists and parses
   - dry_run=true, commit=false, commit_supported=false
   - db_write=false, migration_applied=false, rollback_executed=false
   - collections_touched=[]
   - collections_documented_in_plan includes user_gift_inventory,
     gift_transaction_ledger, hero_affinity_state
   - idempotent_rerun=true
   - borea_rollback_safe=true / borea_activation_allowed=false
   - hidden_aliases_blocked includes borea and primordial_gaia
   - safety_envelope all-false on writes
3. Asserts the script REJECTS --commit (exit code 2).
4. Asserts the script does NOT import motor / pymongo.
"""
from __future__ import annotations
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path('/app')
SCRIPT = ROOT / 'backend' / 'scripts' / 'affinity_phase2_migration_rollback_rehearsal.py'
RESULT = ROOT / 'data' / 'design' / 'affinity' / 'affinity_phase2_rollback_rehearsal_result_v1.json'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


# 1. Script + run
record('script_present', SCRIPT.exists(), str(SCRIPT))
src = SCRIPT.read_text(encoding='utf-8') if SCRIPT.exists() else ''
record('script_no_motor_import',
       not re.search(r'^\s*(import|from)\s+motor', src, re.MULTILINE),
       'motor import forbidden')
record('script_no_pymongo_import',
       not re.search(r'^\s*(import|from)\s+pymongo', src, re.MULTILINE),
       'pymongo import forbidden')
record('script_no_open_write_db',
       not re.search(r'\.insert_one\s*\(|\.update_one\s*\(|\.delete_one\s*\(', src),
       'DB write methods forbidden')

# 2. Run dry-run
try:
    r = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True, text=True, timeout=30,
    )
    record('dry_run_exit_0', r.returncode == 0,
           f'rc={r.returncode}, stderr={r.stderr[:200]}')
except Exception as e:
    record('dry_run_exit_0', False, f'{e!r}')

# 3. Result JSON
record('result_present', RESULT.exists(), str(RESULT))
try:
    res = json.loads(RESULT.read_text(encoding='utf-8'))
    record('result_parses', True, '')
except Exception as e:
    res = {}
    record('result_parses', False, f'{e!r}')

# 4. Invariants
for k, v in [
    ('dry_run', True), ('commit', False), ('commit_supported', False),
    ('db_write', False), ('migration_applied', False),
    ('rollback_executed', False),
    ('idempotent_rerun', True),
    ('borea_rollback_safe', True),
    ('borea_activation_allowed', False),
    ('no_motor_pymongo_import_in_this_script', True),
]:
    record(f'invariant_{k}', res.get(k) == v,
           f'expected {v}, got {res.get(k)!r}')

# collections_touched empty
record('collections_touched_empty',
       res.get('collections_touched') == [], '')

# collections_documented_in_plan complete
cdp = set(res.get('collections_documented_in_plan') or [])
for req in ['user_gift_inventory', 'gift_transaction_ledger',
            'hero_affinity_state']:
    record(f'documented_in_plan:{req}', req in cdp, f'got {cdp}')

# hidden aliases
record('hidden_aliases_blocked',
       set(res.get('hidden_aliases_blocked') or []) >=
       {'borea', 'primordial_gaia'}, '')

# safety_envelope
se = res.get('safety_envelope') or {}
for k in ['db_write', 'inventory_write', 'ledger_write',
          'affinity_points_write', 'feature_flag_currently_enabled']:
    record(f'envelope_{k}_false', se.get(k) is False, f'got {se.get(k)!r}')

# 5. --commit rejected
try:
    r2 = subprocess.run(
        [sys.executable, str(SCRIPT), '--commit'],
        capture_output=True, text=True, timeout=30,
    )
    record('commit_rejected_exit_nonzero', r2.returncode != 0,
           f'expected non-zero, got rc={r2.returncode}')
    record('commit_rejected_fatal_text',
           'reject' in (r2.stderr.lower() + r2.stdout.lower())
           or 'dry-run' in (r2.stderr.lower() + r2.stdout.lower()),
           'expected rejection message')
except Exception as e:
    record('commit_rejected_exit_nonzero', False, f'{e!r}')

# 6. Simulated trace has at least the documented steps count
record('simulated_trace_count_matches_documented',
       res.get('simulated_steps_count') == res.get('documented_steps_count'),
       'simulated_steps must equal documented_steps')

# 7. Ledger ordering documented
record('ledger_ordering_documented',
       res.get('ledger_ordering_documented') is True, '')


print('=' * 70)
print('AF2-F — Affinity Phase 2 Rollback Rehearsal Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
