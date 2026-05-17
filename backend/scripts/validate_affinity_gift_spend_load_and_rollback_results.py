#!/usr/bin/env python3
"""
AF2-L — Validator for the load probe + rollback rehearsal results.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PROBE = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_spend_disabled_load_probe_result_v1.json'
REHEARSAL = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_spend_rollback_rehearsal_result_v1.json'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


record('probe_present', PROBE.exists(), str(PROBE))
record('rehearsal_present', REHEARSAL.exists(), str(REHEARSAL))

p = json.loads(PROBE.read_text(encoding='utf-8'))
record('probe_id', p.get('probe_id') == 'AF2-L-PROBE-001', '')
record('probe_task_af2l', p.get('task_origin') == 'AF2-L', '')
record('probe_design_only', p.get('design_only') is True, '')
record('probe_db_write_false', p.get('db_write') is False, '')
record('probe_no_live_spend', p.get('no_live_spend') is True, '')
record('probe_no_inventory', p.get('no_inventory_mutation') is True, '')
record('probe_no_affinity_pts', p.get('no_affinity_points_mutation') is True, '')
record('probe_no_borea_activation', p.get('no_borea_activation') is True, '')
record('probe_baseline_v6',
       p.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
record('probe_total_ge_40',
       isinstance(p.get('total_requests'), int) and p['total_requests'] >= 40, '')
record('probe_5xx_zero', p.get('total_5xx') == 0, f'got {p.get("total_5xx")}')
record('probe_unexpected_zero',
       p.get('unexpected_total') == 0,
       f'got {p.get("unexpected_total")}')
record('probe_p95_le_500',
       isinstance(p.get('p95_latency_ms'), (int, float))
       and p['p95_latency_ms'] <= 500, f'p95={p.get("p95_latency_ms")}')

by_label = p.get('by_label') or {}
for lbl in ('empty', 'valid', 'dup_idem', 'missing_idem'):
    blk = by_label.get(lbl) or {}
    record(f'label_{lbl}_expected_423',
           blk.get('expected_status') == 423, '')
    record(f'label_{lbl}_no_unexpected',
           blk.get('unexpected_codes') in (None, {}), f'{blk.get("unexpected_codes")}')
for lbl in ('borea', 'greek_borea', 'primordial_gaia'):
    blk = by_label.get(lbl) or {}
    record(f'label_{lbl}_expected_404',
           blk.get('expected_status') == 404, '')
    record(f'label_{lbl}_no_unexpected',
           blk.get('unexpected_codes') in (None, {}), '')

reg = p.get('regression_gets') or {}
for path in ('/affinity/gifts', '/affinity/gifts/summary',
             '/affinity/gifts/by-faction/greek',
             '/affinity/gifts/by-element/dark'):
    record(f'regression:{path}',
           (reg.get(path) or {}).get('code') == 200,
           f'{(reg.get(path) or {})}')

# Rehearsal
r = json.loads(REHEARSAL.read_text(encoding='utf-8'))
record('rehearsal_id', r.get('rehearsal_id') == 'AF2-L-REHEARSAL-001', '')
record('rehearsal_task_af2l', r.get('task_origin') == 'AF2-L', '')
record('rehearsal_design_only', r.get('design_only') is True, '')
record('rehearsal_db_write_false', r.get('db_write') is False, '')
record('rehearsal_destructive_false',
       r.get('destructive_actions_performed') is False, '')
record('rehearsal_dry_run_true', r.get('dry_run') is True, '')
record('rehearsal_steps_min_6',
       isinstance(r.get('rollback_steps'), list)
       and len(r['rollback_steps']) >= 6, '')
record('rehearsal_baseline_v6',
       r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
record('rehearsal_operator_signoff_required',
       r.get('operator_sign_off_required') is True, '')

print('=' * 70)
print('AF2-L — Load Probe + Rollback Rehearsal Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
