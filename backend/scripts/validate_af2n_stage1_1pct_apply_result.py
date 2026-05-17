#!/usr/bin/env python3
"""AF2-N-STAGE1-1PCT-ALLOWLIST APPLY — Result validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/af2n_stage1_1pct_apply_result_v1.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'af2n_stage1_1pct_apply_result_v1', '')
rec('task', r.get('task_origin') == 'AF2-N-STAGE1-1PCT-ALLOWLIST APPLY', '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')

if r.get('stage1_applied') is True:
    rec('preflight_pass', r.get('preflight_status') == 'PASS', '')
    rec('allowlist_size_50', r.get('stage1_allowlist_size') == 50, f"got={r.get('stage1_allowlist_size')}")
    rec('ledger_cap_500', r.get('stage1_ledger_cap') == 500, f"got={r.get('stage1_ledger_cap')}")
    rec('observed_allowlist_50', r.get('observed_allowlist_size') == 50, f"got={r.get('observed_allowlist_size')}")
    rec('observed_cap_500', r.get('observed_ledger_cap') == 500, f"got={r.get('observed_ledger_cap')}")
    rec('post_apply_heroes_100', r.get('post_apply_heroes_count_100') is True, '')
    rec('post_apply_borea_404', r.get('post_apply_borea_404') is True, '')
    rec('post_apply_non_allowlist_423', r.get('post_apply_non_allowlist_423') is True, '')
    rec('overall_state_stage1_active',
        r.get('overall_state') == 'stage1_allowlist_active_no_broad_rollout', '')
    rec('backup_path_present', isinstance(r.get('backup_path'), str)
        and r.get('backup_path').startswith('/app/backups/'), '')
else:
    # blocked path — must record a reason
    rec('blocked_reason_present', isinstance(r.get('stage1_blocked_reason'), str)
        and len(r.get('stage1_blocked_reason')) > 0, '')
    rec('overall_state_not_stage1', r.get('overall_state') != 'stage1_allowlist_active_no_broad_rollout', '')

sf = r.get('safety_flags') or {}
rec('sf_broad_off', sf.get('broad_rollout_authorized') is False, '')
rec('sf_inventory_off', sf.get('inventory_mutation_enabled') is False, '')
rec('sf_battle_off', sf.get('battle_runtime_attached') is False, '')
rec('sf_combat_off', sf.get('applied_to_combat') is False, '')

print('='*70); print('AF2-N-STAGE1-1PCT-ALLOWLIST APPLY — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
