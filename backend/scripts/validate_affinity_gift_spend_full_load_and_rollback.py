#!/usr/bin/env python3
"""AF2-L-FULL — Validator for full load probe + rollback rehearsal results."""
from __future__ import annotations
import json, sys
from pathlib import Path

PROBE = Path('/app/data/design/affinity/affinity_gift_spend_full_disabled_load_result_v1.json')
REH = Path('/app/data/design/affinity/affinity_gift_transaction_ledger_rollback_rehearsal_full_result_v1.json')

failures: list[str] = []; checks: list[tuple[str,bool,str]] = []
def record(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

record('probe_present', PROBE.exists(), str(PROBE))
record('rehearsal_present', REH.exists(), str(REH))

p = json.loads(PROBE.read_text())
record('probe_id', p.get('probe_id') == 'AF2-L-FULL-PROBE-001', '')
record('probe_task', p.get('task_origin') == 'AF2-L-FULL', '')
record('probe_design_only', p.get('design_only') is True, '')
record('probe_db_write_false', p.get('db_write') is False, '')
record('probe_no_live_spend', p.get('no_live_spend') is True, '')
record('probe_baseline_v6', p.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
record('probe_total_ge_120', p.get('total_requests', 0) >= 120, f'got {p.get("total_requests")}')
record('probe_5xx_zero', p.get('total_5xx') == 0, f'got {p.get("total_5xx")}')
record('probe_unexpected_zero', p.get('unexpected_total') == 0, f'got {p.get("unexpected_total")}')
record('probe_p95_le_target', (p.get('p95_latency_ms') or 9999) <= (p.get('p95_target_ms') or 500), f'p95={p.get("p95_latency_ms")}')

by = p.get('by_label') or {}
for lbl in ('empty','valid','no_idem','dup_idem','malformed_idem','negative_qty','huge_qty','stale_gift'):
    b = by.get(lbl) or {}
    record(f'label_{lbl}_expected_423', b.get('expected_status') == 423, '')
    record(f'label_{lbl}_no_unexpected', b.get('unexpected_codes') in (None, {}), str(b.get('unexpected_codes')))
for lbl in ('borea','greek_borea','primordial_gaia'):
    b = by.get(lbl) or {}
    record(f'label_{lbl}_expected_404', b.get('expected_status') == 404, '')
    record(f'label_{lbl}_no_unexpected', b.get('unexpected_codes') in (None, {}), '')

reg = p.get('regression_gets') or {}
for path in ('/affinity/gifts','/affinity/gifts/summary',
             '/affinity/gifts/by-faction/greek','/affinity/gifts/by-element/dark',
             '/affinity/gifts/by-element/darkness'):
    record(f'regression:{path}', (reg.get(path) or {}).get('code') == 200, f'{reg.get(path)}')

r = json.loads(REH.read_text())
record('rehearsal_id', r.get('rehearsal_id') == 'AF2-L-FULL-REHEARSAL-001', '')
record('rehearsal_task', r.get('task_origin') == 'AF2-L-FULL', '')
record('rehearsal_design_only', r.get('design_only') is True, '')
record('rehearsal_db_write_false', r.get('db_write') is False, '')
record('rehearsal_destructive_false', r.get('destructive_actions_performed') is False, '')
record('rehearsal_dry_run', r.get('dry_run') is True, '')
record('rehearsal_steps_min_8', len(r.get('rollback_steps') or []) >= 8, '')
record('rehearsal_operator_signoff', r.get('operator_sign_off_required') is True, '')
record('rehearsal_commit_state_referenced',
       isinstance(r.get('commit_state_referenced'), dict) and 'migration_applied' in r['commit_state_referenced'], '')

print('='*70); print('AF2-L-FULL — Load + Rollback Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
