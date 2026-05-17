#!/usr/bin/env python3
"""AF2-N FINAL-USER-RUNTIME-APPROVAL record validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/final_user_runtime_approval_record_v1.json')
failures: list[str] = []
checks: list[tuple[str,bool,str]] = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('record_present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('record_id') == 'final_user_runtime_approval_record_v1', '')
rec('task', r.get('task_origin') == 'AF2-N FINAL-USER-RUNTIME-APPROVAL', '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('approval_present', r.get('final_user_runtime_approval_present') is True, '')
rec('approval_quoted', isinstance(r.get('user_approval_message_quoted'), str)
    and 'procediamo' in r.get('user_approval_message_quoted',''), '')
rec('approval_scope_min_3', len(r.get('user_approval_scope') or []) >= 3, '')
rec('not_authorizing_min_4', len(r.get('user_approval_NOT_authorizing') or []) >= 4, '')
rec('all_5_signoffs_true', r.get('all_5_operator_signoffs_true') is True, '')

conf = r.get('canary_configuration_executed') or {}
rec('canary_runtime_flag', conf.get('AFFINITY_GIFT_RUNTIME_ENABLED') == 'true_explicit_affinity_gift_runtime_on', '')
rec('canary_allowlist_size', conf.get('allowlist_size', 0) >= 1, '')
rec('canary_cap_present', isinstance(conf.get('hard_cap'), int) and conf.get('hard_cap') > 0, '')

sf = r.get('safety_flags') or {}
rec('sf_canary_only', sf.get('runtime_attached_canary_only') is True, '')
rec('sf_inventory_off', sf.get('inventory_mutation_enabled') is False, '')
rec('sf_affinity_points_off', sf.get('affinity_points_mutation_enabled') is False, '')
rec('sf_buffs_off', sf.get('buffs_enabled') is False, '')
rec('sf_battle_off', sf.get('battle_runtime_attached') is False, '')
rec('sf_combat_off', sf.get('applied_to_combat') is False, '')
rec('sf_borea_blocked', sf.get('hidden_aliases_blocked') == ['borea','greek_borea','primordial_gaia'], '')
rec('sf_broad_rollout_off', sf.get('broad_rollout_authorized') is False, '')

print('='*70); print('AF2-N FINAL-USER-RUNTIME-APPROVAL — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
