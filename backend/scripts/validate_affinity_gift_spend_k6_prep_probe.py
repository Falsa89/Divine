#!/usr/bin/env python3
"""AF2-L-K6-PREP/FULL-SAFE — Validator for the prep-probe result."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/affinity_gift_spend_k6_prep_probe_result_v1.json')
PYSUB_RESULT = Path('/app/data/design/affinity/affinity_gift_spend_full_disabled_load_result_v1.json')

failures: list[str] = []
checks: list[tuple[str,bool,str]] = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('result_present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('result_id', r.get('result_id') == 'affinity_gift_spend_k6_prep_probe_result_v1', '')
rec('task_origin', r.get('task_origin') == 'AF2-L-K6-PREP/FULL-SAFE', '')
rec('design_only', r.get('design_only') is True, '')
rec('runtime_off', r.get('runtime_attached') is False, '')
rec('db_write_off', r.get('db_write') is False, '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')

mode = r.get('mode') or ''
rec('mode_accepted', mode in (
    'plan_only_tool_unavailable',
    'safe_disabled_probe_executed',
    'plan_only_tool_unavailable_AND_safe_disabled_probe_executed'
), f'got mode={mode!r}')

rec('python_substitute_executed', r.get('python_substitute_executed') is True, '')
rec('python_substitute_result_present', PYSUB_RESULT.exists(), str(PYSUB_RESULT))

acc = r.get('acceptance') or {}
rec('acc_no_real_spend', acc.get('no_real_spend') is True, '')
rec('acc_no_db_write', acc.get('no_db_write') is True, '')
rec('acc_endpoint_disabled', acc.get('endpoint_remained_disabled') is True, '')
rec('acc_borea_404', acc.get('borea_remained_404') is True, '')

m = r.get('observed_metrics_from_python_substitute') or {}
rec('metric_5xx_zero', m.get('http_5xx_count') == 0, f"got {m.get('http_5xx_count')}")
rec('metric_unexpected_zero', m.get('unexpected_status_count') == 0, f"got {m.get('unexpected_status_count')}")
rec('metric_endpoint_423', m.get('endpoint_status_for_empty_post') == 423, '')
rec('metric_borea_404', m.get('endpoint_status_for_borea_alias') == 404, '')

sf = r.get('safety_flags') or {}
rec('sf_runtime_off', sf.get('runtime_attached') is False, '')
rec('sf_db_write_off', sf.get('db_write') is False, '')
rec('sf_flag_off', sf.get('feature_flag_currently_enabled') is False, '')
rec('sf_af2n_blocked', sf.get('AF2N_allowed_today') is False, '')

# Cross-check the python substitute result
if PYSUB_RESULT.exists():
    s = json.loads(PYSUB_RESULT.read_text())
    rec('pysub_5xx_zero', s.get('total_5xx') == 0, f"got {s.get('total_5xx')}")
    rec('pysub_unexpected_zero', s.get('unexpected_total') == 0, f"got {s.get('unexpected_total')}")

print('='*70); print('AF2-L-K6-PREP/FULL-SAFE — Prep probe validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
