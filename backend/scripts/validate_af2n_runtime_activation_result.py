#!/usr/bin/env python3
"""AF2-N runtime activation result validator."""
from __future__ import annotations
import json, sys
from pathlib import Path
R = Path('/app/data/design/affinity/af2n_runtime_activation_result_v1.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')
rec('present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'af2n_runtime_activation_result_v1', '')
rec('task', r.get('task_origin') == 'AF2-N CONTROLLED RUNTIME FLIP CANARY', '')
rec('runtime_attached_true', r.get('runtime_attached') is True, '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
ev = r.get('env_vars_set_in_supervisor') or {}
rec('env_runtime_flag', ev.get('AFFINITY_GIFT_RUNTIME_ENABLED') == 'true_explicit_affinity_gift_runtime_on', '')
rec('env_allowlist_set', isinstance(ev.get('AFFINITY_GIFT_CANARY_ALLOWLIST'), str) and len(ev.get('AFFINITY_GIFT_CANARY_ALLOWLIST',''))>0, '')
rec('env_cap_set', isinstance(ev.get('AFFINITY_GIFT_CANARY_LEDGER_CAP'), str), '')
rec('allowlist_size_min_1', r.get('allowlist_size', 0) >= 1, '')
rec('cap_positive', r.get('canary_ledger_cap', 0) > 0, '')
rec('total_rows_below_cap', r.get('ledger_total_rows', 999) < r.get('canary_ledger_cap', 0), '')
rec('only_canary_writes', r.get('ledger_total_rows') == r.get('ledger_canary_rows'), '')
rec('idem_replay_no_dup', r.get('idempotent_replay_verified_no_duplicate_insert') is True, '')
rec('non_allowlist_blocked', r.get('non_allowlist_user_still_423') is True, '')
rec('borea_still_404', r.get('borea_aliases_still_404') is True, '')
rec('heroes_count_100', r.get('api_heroes_count_still_100') is True, '')
rec('battle_unchanged', r.get('battle_files_unchanged') is True, '')
rec('rollback_script_path_set', isinstance(r.get('rollback_script_path'), str), '')
sf = r.get('safety_flags') or {}
rec('sf_canary_only', sf.get('runtime_attached_canary_only') is True, '')
rec('sf_broad_rollout_off', sf.get('broad_rollout_authorized') is False, '')
rec('sf_db_scope', 'gift_transaction_ledger' in (sf.get('db_write_scope') or ''), '')
rec('sf_inventory_off', sf.get('inventory_mutation_enabled') is False, '')
rec('sf_points_off', sf.get('affinity_points_mutation_enabled') is False, '')
rec('sf_buffs_off', sf.get('buffs_enabled') is False, '')
rec('sf_battle_off', sf.get('battle_runtime_attached') is False, '')
rec('sf_combat_off', sf.get('applied_to_combat') is False, '')
rec('sf_flag_on', sf.get('feature_flag_currently_enabled') is True, '')
rec('sf_borea_blocked', sf.get('hidden_aliases_blocked') == ['borea','greek_borea','primordial_gaia'], '')
rows = r.get('ledger_rows_dump') or []
rec('dump_min_1_row', len(rows) >= 1, '')
for row in rows:
    assert isinstance(row, dict)
    if row.get('inventory_mutated') is not False or row.get('affinity_points_mutated') is not False or \
       row.get('buffs_activated') is not False or row.get('battle_wiring_attached') is not False or \
       (row.get('hero_id') or '') in ('borea','greek_borea','primordial_gaia'):
        rec(f'row_safe_{row.get("tx_id")}', False, f'row violates safety: {row}')
rec('all_rows_safe', all(
    row.get('inventory_mutated') is False and row.get('affinity_points_mutated') is False
    and row.get('buffs_activated') is False and row.get('battle_wiring_attached') is False
    and (row.get('hero_id') or '') not in ('borea','greek_borea','primordial_gaia')
    for row in rows
), '')

print('='*70); print('AF2-N RUNTIME ACTIVATION RESULT — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
