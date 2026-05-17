#!/usr/bin/env python3
"""
SAFETY-ROLLUP-A — Validator for the runtime activation readiness rollup.

Verifies:
  - rollup file present + parses
  - activation_ready=false / design_preview_ready=true / go_no_go_decision=NO_GO
  - all 5 subsystems listed (collection, affinity, cap_resolver, axis, skill_kit)
  - blocking_gates_unsatisfied >= 5 with explicit ids
  - invariants_currently_holding all true
  - feature flags all OFF in current state
  - cross-check with the AXIS-D activation table file
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
ROLLUP = ROOT / 'data' / 'design' / 'system_safety' / 'runtime_activation_readiness_rollup_v1.json'
AXIS_TABLE = ROOT / 'data' / 'design' / 'shared' / 'canonical_axis_activation_validation_table_v1.json'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


record('rollup_present', ROLLUP.exists(), str(ROLLUP))
r = json.loads(ROLLUP.read_text(encoding='utf-8'))
record('report_id', r.get('report_id') == 'runtime_activation_readiness_rollup_v1', '')
record('task_origin', r.get('task_origin') == 'SAFETY-ROLLUP-A', '')
for k, v in [('design_only', True), ('runtime_attached', False),
             ('db_write', False), ('activation_ready', False),
             ('design_preview_ready', True),
             ('go_no_go_decision', 'NO_GO'),
             ('no_borea_activation', True)]:
    record(f'flag_{k}', r.get(k) == v, f'expected {v}, got {r.get(k)!r}')

ss = r.get('subsystems') or {}
for required in ['collection_synergy_v2', 'affinity_phase_2',
                 'global_cap_resolver', 'axis', 'skill_kit_runtime_adapter']:
    record(f'subsystem_present:{required}', required in ss, '')
# All feature flags must be currently_enabled=False
for sub_id, sub in ss.items():
    if isinstance(sub, dict) and 'feature_flag_currently_enabled' in sub:
        record(f'subsystem_flag_off:{sub_id}',
               sub.get('feature_flag_currently_enabled') is False, '')

gates = r.get('blocking_gates_unsatisfied') or []
record('blocking_gates_min_5', len(gates) >= 5, f'got {len(gates)}')
ids = {g.get('id') for g in gates if isinstance(g, dict)}
for req in ['axis_d_activation_ready_false', 'af2_i_auth_ratelimit_wiring_missing',
            'af2_d_migration_not_executed', 'global_cap_resolver_not_wired',
            'baseline_v6_not_created']:
    record(f'gate_present:{req}', req in ids, '')

inv = r.get('invariants_currently_holding') or {}
for k in ['api_heroes_count_100', 'borea_hidden', 'feature_flags_all_off',
          'runtime_adapter_off', 'battle_engine_unchanged',
          'combat_tsx_unchanged', 'baseline_v5_clean',
          'rm134b_unchanged', 'af2a_unchanged',
          'gacha_unchanged', 'roster_unchanged']:
    record(f'invariant_holds:{k}', inv.get(k) is True, '')

# Cross-check with AXIS-D table
if AXIS_TABLE.exists():
    at = json.loads(AXIS_TABLE.read_text(encoding='utf-8'))
    record('axis_d_table_activation_ready_false',
           at.get('activation_ready') is False, '')
    record('rollup_axis_subsystem_consistent',
           ss.get('axis', {}).get('activation_ready') is False, '')

rec_seq = r.get('recommended_unblock_sequence') or []
record('recommended_unblock_sequence_min_8', len(rec_seq) >= 8,
       f'got {len(rec_seq)}')

print('=' * 70)
print('SAFETY-ROLLUP-A — Runtime Activation Readiness Rollup Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
