#!/usr/bin/env python3
"""AF2-N-STAGE1-PREP — Plan validator (NOT a stage1 apply)."""
from __future__ import annotations
import json, sys
from pathlib import Path
P = Path('/app/data/design/affinity/af2n_stage1_1pct_allowlist_plan_v1.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('present', P.exists(), str(P))
p = json.loads(P.read_text())
rec('id', p.get('plan_id') == 'af2n_stage1_1pct_allowlist_plan_v1', '')
rec('task', p.get('task_origin') == 'AF2-N-STAGE1-PREP (plan only, NOT applied)', '')
rec('design_only', p.get('design_only') is True, '')
rec('do_not_apply', p.get('do_not_apply_in_this_task') is True, '')
rec('db_write_off', p.get('db_write') is False, '')
rec('baseline_v6', p.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')

cs = p.get('current_state') or {}
rec('cs_canary_active', cs.get('canary_active') is True, '')
rec('cs_allowlist_3', cs.get('allowlist_size_today') == 3, '')

ts = p.get('stage1_target_state') or {}
rec('target_allowlist_cap', ts.get('allowlist_size_hard_cap', 0) >= 50, '')
rec('target_ledger_cap', isinstance(ts.get('canary_ledger_cap_proposed'), int)
    and ts.get('canary_ledger_cap_proposed') > 20, '')
rec('selection_criteria_min_3', len(ts.get('selection_criteria') or []) >= 3, '')

pre = p.get('prerequisites_required_BEFORE_stage1_apply') or []
rec('prereqs_min_5', len(pre) >= 5, '')
stage1_approval = next((g for g in pre if g.get('id') == 'explicit_user_stage1_approval'), None)
rec('stage1_approval_required', stage1_approval is not None and stage1_approval.get('required') is True, '')
rec('stage1_approval_status_fail', stage1_approval is not None
    and stage1_approval.get('status_today', '').startswith('FAIL'), '')

rec('abort_triggers_min_5', len(p.get('abort_triggers_stage1') or []) >= 5, '')
rec('apply_procedure_documented', len(p.get('stage1_apply_procedure_DO_NOT_EXECUTE') or []) >= 6, '')
rec('rollback_procedure_documented', len(p.get('stage1_rollback_procedure') or []) >= 2, '')
rec('safety_constraints_min_5', len(p.get('safety_constraints') or []) >= 5, '')

sf = p.get('safety_flags') or {}
rec('sf_canary_only', sf.get('runtime_attached_canary_only') is True, '')
rec('sf_stage1_not_applied', sf.get('stage1_applied') is False, '')
rec('sf_broad_rollout_off', sf.get('broad_rollout_authorized') is False, '')
rec('sf_inventory_off', sf.get('inventory_mutation_enabled') is False, '')
rec('sf_points_off', sf.get('affinity_points_mutation_enabled') is False, '')
rec('sf_buffs_off', sf.get('buffs_enabled') is False, '')
rec('sf_battle_off', sf.get('battle_runtime_attached') is False, '')

print('='*70); print('AF2-N-STAGE1-PREP — Plan Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
