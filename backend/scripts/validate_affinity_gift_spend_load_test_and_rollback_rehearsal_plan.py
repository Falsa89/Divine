#!/usr/bin/env python3
"""
AF2-L-PRE — Validator for the load test + rollback rehearsal plan.

Verifies the plan is design-only, no execution occurred in this task,
and the structural requirements are present.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

PLAN = Path('/app/data/design/affinity/'
            'affinity_gift_spend_load_test_and_rollback_rehearsal_plan_v1.json')

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


record('plan_present', PLAN.exists(), str(PLAN))
p = json.loads(PLAN.read_text(encoding='utf-8')) if PLAN.exists() else {}
record('plan_id',
       p.get('plan_id') == 'affinity_gift_spend_load_test_and_rollback_rehearsal_plan_v1', '')
record('task_origin', p.get('task_origin') == 'AF2-L-PRE', '')
record('design_only', p.get('design_only') is True, '')
record('runtime_attached_false', p.get('runtime_attached') is False, '')
record('db_write_false', p.get('db_write') is False, '')
record('no_borea_activation', p.get('no_borea_activation') is True, '')
record('baseline_v6',
       p.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')

lt = p.get('load_test_targets') or {}
record('lt_endpoint_gift_spend',
       lt.get('endpoint') == 'POST /api/affinity/gift-spend', '')
record('lt_vu_ge_50',
       isinstance(lt.get('concurrent_virtual_users'), int)
       and lt['concurrent_virtual_users'] >= 50, '')
record('lt_duration_min_ge_5',
       isinstance(lt.get('duration_minutes'), int)
       and lt['duration_minutes'] >= 5, '')
record('lt_borea_injection_ge_1pct',
       lt.get('borea_alias_injection_rate_percent', 0) >= 1, '')
record('lt_idem_replay_ge_5pct',
       lt.get('idempotency_replay_rate_percent', 0) >= 5, '')

ac = p.get('acceptance_thresholds') or {}
record('ac_p95_le_500', ac.get('p95_latency_ms_max', 9999) <= 500, '')
record('ac_5xx_le_1pct', ac.get('error_rate_5xx_max_percent', 99) <= 1, '')
record('ac_borea_404_100', ac.get('borea_404_correctness_percent_min', 0) >= 100, '')
record('ac_no_duplicate_charge',
       ac.get('duplicate_charge_rate_percent_max', 99) == 0, '')

rb = p.get('rollback_rehearsal') or {}
record('rb_id_rehearsal_001',
       rb.get('rehearsal_id') == 'AF2-L-REHEARSAL-001', '')
record('rb_flip_off_le_30',
       isinstance(rb.get('flag_flip_to_off_in_seconds_max'), int)
       and rb['flag_flip_to_off_in_seconds_max'] <= 30, '')
record('rb_steps_min_4',
       isinstance(rb.get('rollback_steps'), list)
       and len(rb['rollback_steps']) >= 4, '')
record('rb_operator_sign_off_required',
       rb.get('operator_sign_off_required') is True, '')

record('pre_conditions_min_3',
       isinstance(p.get('pre_conditions'), list)
       and len(p['pre_conditions']) >= 3, '')
record('post_conditions_min_3',
       isinstance(p.get('post_conditions'), list)
       and len(p['post_conditions']) >= 3, '')

sf = p.get('safety_flags') or {}
record('sf_load_test_not_executed',
       sf.get('load_test_executed_in_this_task') is False, '')
record('sf_rollback_not_executed',
       sf.get('rollback_rehearsal_executed_in_this_task') is False, '')
record('sf_db_write_false', sf.get('db_write') is False, '')
record('sf_feature_flag_off',
       sf.get('feature_flag_currently_enabled') is False, '')


print('=' * 70)
print('AF2-L-PRE — Load Test + Rollback Rehearsal Plan Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
