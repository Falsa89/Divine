#!/usr/bin/env python3
"""AF2-L-K6-LIVE-PREP — Validator for the V2 prep result."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/affinity_gift_spend_k6_live_prep_result_v2.json')
failures: list[str] = []
checks: list[tuple[str,bool,str]] = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('result_present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'affinity_gift_spend_k6_live_prep_result_v2', '')
rec('task', r.get('task_origin') == 'AF2-L-K6-LIVE-PREP/FULL-SAFE', '')
rec('design_only', r.get('design_only') is True, '')
rec('runtime_off', r.get('runtime_attached') is False, '')
rec('db_write_off', r.get('db_write') is False, '')
rec('no_live_spend', r.get('no_live_spend') is True, '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('total_5xx_zero', r.get('total_5xx') == 0, f"got {r.get('total_5xx')}")
rec('unexpected_total_zero', r.get('unexpected_total') == 0, f"got {r.get('unexpected_total')}")
rec('regression_unexpected_zero', r.get('regression_unexpected') == 0, f"got {r.get('regression_unexpected')}")
rec('total_requests_min_300', r.get('total_requests', 0) >= 300, f"got {r.get('total_requests')}")
rec('p95_within_target', r.get('p95_latency_ms', 9999) <= r.get('p95_target_ms', 500), f"p95={r.get('p95_latency_ms')}")
rec('ledger_rows_zero', r.get('ledger_rows_after_run') in (0, None), f"got {r.get('ledger_rows_after_run')}")
rec('mode_accepted', r.get('mode') in (
    'plan_only_tool_unavailable',
    'safe_disabled_probe_executed',
    'plan_only_tool_unavailable_AND_safe_disabled_probe_executed',
    'k6_installed_safe_run_executed',
    'locust_installed_safe_run_executed'), f"mode={r.get('mode')!r}")

by = r.get('by_label') or {}
for lbl in ('empty','valid','no_idem','dup_idem','malformed_idem','negative_qty','huge_qty','stale_gift'):
    rec(f'label_{lbl}_expected_423', (by.get(lbl) or {}).get('expected_status') == 423, '')
    rec(f'label_{lbl}_no_unexpected', (by.get(lbl) or {}).get('unexpected_codes') == {}, f"got {(by.get(lbl) or {}).get('unexpected_codes')}")
for lbl in ('borea','greek_borea','primordial_gaia'):
    rec(f'label_{lbl}_expected_404', (by.get(lbl) or {}).get('expected_status') == 404, '')
    rec(f'label_{lbl}_no_unexpected', (by.get(lbl) or {}).get('unexpected_codes') == {}, '')

reg = r.get('regression_gets') or {}
rec('regression_count_min_8', len(reg) >= 8, f'got {len(reg)}')
for path, info in reg.items():
    rec(f'regression_{path}_ok', info.get('ok') is True, f"got code={info.get('code')} expected={info.get('expected')}")

sf = r.get('safety_flags') or {}
rec('sf_runtime_off', sf.get('runtime_attached') is False, '')
rec('sf_db_write_off', sf.get('db_write') is False, '')
rec('sf_flag_off', sf.get('feature_flag_currently_enabled') is False, '')
rec('sf_af2n_blocked', sf.get('AF2N_allowed_today') is False, '')

print('='*70); print('AF2-L-K6-LIVE-PREP v2 — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
