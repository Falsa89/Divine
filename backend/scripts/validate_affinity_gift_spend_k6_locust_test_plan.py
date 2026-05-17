#!/usr/bin/env python3
"""AF2-L-K6-PREP — Validator for the k6/Locust test plan + assets."""
from __future__ import annotations
import json, sys
from pathlib import Path

PLAN = Path('/app/data/design/affinity/affinity_gift_spend_k6_locust_test_plan_v1.json')
K6   = Path('/app/loadtests/affinity_gift_spend_disabled.k6.js')
LOC  = Path('/app/loadtests/affinity_gift_spend_disabled_locust.py')
PYSUB = Path('/app/backend/scripts/run_affinity_gift_spend_full_disabled_load_probe.py')

failures: list[str] = []
checks: list[tuple[str,bool,str]] = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('plan_present', PLAN.exists(), str(PLAN))
rec('k6_present', K6.exists(), str(K6))
rec('locust_present', LOC.exists(), str(LOC))
rec('python_substitute_present', PYSUB.exists(), str(PYSUB))

p = json.loads(PLAN.read_text())
rec('plan_id', p.get('plan_id') == 'affinity_gift_spend_k6_locust_test_plan_v1', '')
rec('task_origin', p.get('task_origin') == 'AF2-L-K6-PREP', '')
rec('design_only', p.get('design_only') is True, '')
rec('runtime_off', p.get('runtime_attached') is False, '')
rec('db_write_off', p.get('db_write') is False, '')
rec('baseline_v6', p.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('endpoint_disabled_423', p.get('endpoint_expected_status_disabled') == 423, '')
rec('endpoint_borea_404', p.get('endpoint_expected_status_borea_alias') == 404, '')
rec('profiles_3', len(p.get('profiles') or []) == 3, '')
rec('safety_constraints_min_5', len(p.get('safety_constraints') or []) >= 5, '')
rec('invariants_before_min_5', len(p.get('required_invariants_before_run') or []) >= 5, '')
rec('invariants_after_min_3', len(p.get('required_invariants_after_run') or []) >= 3, '')

k6_src = K6.read_text()
rec('k6_targets_gift_spend', '/affinity/gift-spend' in k6_src, '')
rec('k6_asserts_423', '423' in k6_src, '')
rec('k6_asserts_borea_404', '404' in k6_src and 'borea' in k6_src.lower(), '')
rec('k6_no_real_spend_keyword', ('commit' not in k6_src.lower()) and 'enableruntime' not in k6_src.lower(), '')

loc_src = LOC.read_text()
rec('locust_targets_gift_spend', '/api/affinity/gift-spend' in loc_src, '')
rec('locust_asserts_423', '423' in loc_src, '')
rec('locust_asserts_borea_404', '404' in loc_src and 'borea' in loc_src.lower(), '')

sf = p.get('safety_flags') or {}
rec('sf_runtime_off', sf.get('runtime_attached') is False, '')
rec('sf_db_write_off', sf.get('db_write') is False, '')
rec('sf_flag_off', sf.get('feature_flag_currently_enabled') is False, '')
rec('sf_af2n_blocked', sf.get('AF2N_allowed_today') is False, '')
rec('sf_borea_blocked', sf.get('hidden_aliases_blocked') == ['borea','greek_borea','primordial_gaia'], '')

print('='*70); print('AF2-L-K6-PREP — Test plan validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
