#!/usr/bin/env python3
"""AF2-M-SIGN-PRE — Validator for operator signoff package v2."""
from __future__ import annotations
import json, sys
from pathlib import Path
PACK = Path('/app/data/design/affinity/affinity_gift_runtime_operator_signoff_package_v2.json')

failures: list[str] = []; checks: list[tuple[str,bool,str]] = []
def record(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

record('package_present', PACK.exists(), str(PACK))
p = json.loads(PACK.read_text())
record('package_id_v2', p.get('package_id') == 'affinity_gift_runtime_operator_signoff_package_v2', '')
record('task_af2m_sign_pre', p.get('task_origin') == 'AF2-M-SIGN-PRE', '')
record('supersedes_v1', p.get('supersedes') == 'affinity_gift_runtime_operator_signoff_package_v1', '')
record('design_only', p.get('design_only') is True, '')
record('runtime_attached_false', p.get('runtime_attached') is False, '')
record('db_write_false', p.get('db_write') is False, '')
record('no_borea_activation', p.get('no_borea_activation') is True, '')
record('baseline_v6', p.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')

so = p.get('signoffs') or {}
for f in ('product_signoff','engineering_signoff','qa_signoff','economy_balance_signoff','rollback_owner_signoff'):
    record(f'signoff_false:{f}', so.get(f) is False, '')
record('af2n_allowed_false', p.get('af2n_allowed') is False, '')
record('feature_flag_off', p.get('feature_flag_currently_enabled') is False, '')
record('explicit_user_approval', p.get('explicit_user_approval_required') is True, '')

up = p.get('upstream_results') or {}
record('upstream_af2k_ref', up.get('af2k_commit_result_ref') == 'affinity_gift_transaction_ledger_migration_commit_result_v1', '')
record('upstream_af2k_rows_zero', up.get('af2k_rows_inserted') == 0, '')
record('upstream_af2l_ref', up.get('af2l_full_probe_ref') == 'affinity_gift_spend_full_disabled_load_result_v1', '')
record('upstream_af2l_probe_pass', up.get('af2l_full_probe_pass') is True, '')
record('upstream_af2l_rehearsal_pass', up.get('af2l_full_rehearsal_pass') is True, '')

pre = p.get('preconditions') or []
record('preconditions_min_15', len(pre) >= 15, f'got {len(pre)}')
pre_ids = {x.get('id') for x in pre}
for req in ('af2k_commit_safe','af2l_full_load_probe_pass','af2l_full_rollback_rehearsal_pass',
            'axis_g_routes_pass','ops_c_wiring_pass'):
    record(f'precondition:{req}', req in pre_ids, '')

trig = p.get('immediate_rollback_triggers') or []
record('triggers_min_5', len(trig) >= 5, '')
stages = p.get('rollout_stages') or []
record('stages_min_5', len(stages) >= 5, '')
record('only_stage0_allowed',
       all(s.get('allowed_today') is (s.get('id','').startswith('stage0')) for s in stages), '')

gate = p.get('go_decision_gate') or {}
record('gate_user_approval', gate.get('user_explicit_approval_required') is True, '')
record('gate_all_signoffs_false', gate.get('all_signoffs_true') is False, '')
record('gate_af2k_commit_required', gate.get('af2k_commit_applied_required') is True, '')
record('gate_af2l_full_required', gate.get('af2l_full_load_pass_required') is True, '')

sf = p.get('safety_flags') or {}
record('sf_runtime_attached_false', sf.get('runtime_attached') is False, '')
record('sf_db_write_false', sf.get('db_write') is False, '')
record('sf_af2n_blocked', sf.get('af2n_allowed_today') is False, '')

print('='*70); print('AF2-M-SIGN-PRE — Sign-off Package v2 Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
