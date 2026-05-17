#!/usr/bin/env python3
"""AF2-L-K6-PREP3 — K6 test plan validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

P = Path('/app/data/design/affinity/af2n_stage1_k6_live_test_plan_v1.json')
K6 = Path('/app/loadtests/af2n_stage1_allowlist.k6.js')
LOC = Path('/app/loadtests/af2n_stage1_allowlist_locust.py')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('plan_present', P.exists(), str(P))
p = json.loads(P.read_text())
rec('id', p.get('plan_id') == 'af2n_stage1_k6_live_test_plan_v1', '')
rec('task', p.get('task_origin') == 'AF2-L-K6-PREP3', '')
rec('design_only', p.get('design_only') is True, '')
rec('db_write_false', p.get('db_write') is False, '')
rec('baseline_v6', p.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('k6_script_path_exists', K6.exists(), str(K6))
rec('locust_script_path_exists', LOC.exists(), str(LOC))
rec('mode_fallback', 'plan_only_python_fallback_used' in p.get('mode',''), '')
prof = p.get('profile') or {}
rec('vus_min_1', prof.get('vus', 0) >= 1, '')
rec('endpoints_min_5', len(prof.get('endpoints_probed') or []) >= 5, '')
rec('thresholds_p95_500', (prof.get('thresholds') or {}).get('p95_latency_ms_lt') == 500, '')
rec('abort_triggers_min_3', len(prof.get('abort_triggers') or []) >= 3, '')
rec('safety_constraints_min_5', len(p.get('safety_constraints') or []) >= 5, '')
sf = p.get('safety_flags') or {}
for k in ('broad_rollout_authorized','inventory_mutation_enabled','affinity_points_mutation_enabled',
          'buffs_enabled','battle_runtime_attached','applied_to_combat'):
    rec(f'sf_{k}_false', sf.get(k) is False, '')
rec('sf_stage1_only', sf.get('runtime_attached_stage1_allowlist_only') is True, '')
rec('sf_flag_on', sf.get('feature_flag_currently_enabled') is True, '')

print('='*70); print('AF2-L-K6-PREP3 — Plan Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
