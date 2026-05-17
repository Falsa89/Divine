#!/usr/bin/env python3
"""AF2-N-STAGE1-EXTENDED-MONITORING-V15 — Validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/af2n_stage1_extended_monitoring_v15_result.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'af2n_stage1_extended_monitoring_v15_result', '')
rec('task', r.get('task_origin') == 'AF2-N-STAGE1-EXTENDED-MONITORING-V15', '')
rec('stage1_only', r.get('runtime_attached_stage1_allowlist_only') is True, '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('samples_min_60', r.get('samples', 0) >= 60, '')
rec('triggers_zero', r.get('triggers_total', 99) == 0, f"triggers={r.get('triggers_fired')}")
rec('overall_pass', r.get('overall_status') == 'PASS', '')
rec('5xx_zero', r.get('any_5xx_total', 99) == 0, '')
rec('ledger_delta_ok', r.get('ledger_row_count_unchanged_or_small_delta') is True,
    f"before={r.get('ledger_row_count_before')} after={r.get('ledger_row_count_after')}")
rec('ledger_delta_le_5', (r.get('ledger_row_count_after', 0) - r.get('ledger_row_count_before', 0)) <= 5, '')

cs = r.get('codes') or {}
for label, ok_codes in [('borea',['404']),('nonal',['423']),('replay',['200'])]:
    obs = cs.get(label) or {}
    rec(f'codes_{label}_clean', all(k in ok_codes for k in obs.keys()) and bool(obs), f'got {obs}')
for label in ('health','heroes','status'):
    obs = cs.get(label) or {}
    rec(f'codes_{label}_200', obs.get('200', 0) >= r.get('samples', 0), f'got {obs}')

sf = r.get('safety_flags') or {}
for k in ('broad_rollout_authorized','inventory_mutation_enabled','affinity_points_mutation_enabled',
          'buffs_enabled','battle_runtime_attached','applied_to_combat'):
    rec(f'sf_{k}_false', sf.get(k) is False, '')
rec('sf_stage1_only', sf.get('runtime_attached_stage1_allowlist_only') is True, '')

print('='*70); print('AF2-N-STAGE1-EXTENDED-MONITORING-V15 — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
