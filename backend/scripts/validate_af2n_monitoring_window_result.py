#!/usr/bin/env python3
"""AF2-N-MONITORING-WINDOW — Result validator."""
from __future__ import annotations
import json, sys
from pathlib import Path
R = Path('/app/data/design/affinity/af2n_monitoring_window_result_v1.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'af2n_monitoring_window_result_v1', '')
rec('task', r.get('task_origin') == 'AF2-N-MONITORING-WINDOW', '')
rec('canary_only', r.get('runtime_attached_canary_only') is True, '')
rec('db_write_off', r.get('db_write') is False, '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('samples_min_20', r.get('samples', 0) >= 20, '')
rec('triggers_zero', r.get('triggers_total', 99) == 0, f"triggers={r.get('triggers_fired')}")
rec('overall_pass', r.get('overall_status') == 'PASS', '')
rec('any_5xx_zero', r.get('any_5xx_total', 99) == 0, '')
rec('inventory_mut_zero', r.get('ledger_inventory_mutation_count') == 0, '')
rec('points_mut_zero', r.get('ledger_affinity_points_mutation_count') == 0, '')
rec('buffs_zero', r.get('ledger_buffs_activation_count') == 0, '')
rec('battle_wire_zero', r.get('ledger_battle_wiring_count') == 0, '')
rec('borea_hero_zero', r.get('ledger_borea_hero_count') == 0, '')
rec('only_canary_rows', r.get('ledger_total_rows') == r.get('ledger_canary_rows'), '')

sc = r.get('spend_empty_codes') or {}
rec('spend_empty_all_423', sc.get('423', 0) >= r.get('samples', 0), f'got {sc}')
bc = r.get('spend_borea_codes') or {}
rec('spend_borea_all_404', bc.get('404', 0) >= r.get('samples', 0), f'got {bc}')
nc = r.get('spend_nonal_codes') or {}
rec('spend_nonal_no_200', nc.get('200', 0) == 0, f'got {nc}')
rc = r.get('spend_replay_codes') or {}
rec('spend_replay_200', rc.get('200', 0) >= r.get('samples', 0), f'got {rc}')
hcs = r.get('heroes_codes') or {}
rec('heroes_all_200_or_304', sum(c for k, c in hcs.items() if k in ('200','304')) >= r.get('samples', 0), f'got {hcs}')

sf = r.get('safety_flags') or {}
rec('sf_canary_only', sf.get('runtime_attached_canary_only') is True, '')
rec('sf_broad_rollout_off', sf.get('broad_rollout_authorized') is False, '')
rec('sf_inventory_off', sf.get('inventory_mutation_enabled') is False, '')
rec('sf_points_off', sf.get('affinity_points_mutation_enabled') is False, '')
rec('sf_buffs_off', sf.get('buffs_enabled') is False, '')
rec('sf_battle_off', sf.get('battle_runtime_attached') is False, '')
rec('sf_combat_off', sf.get('applied_to_combat') is False, '')
rec('sf_borea_blocked', sf.get('hidden_aliases_blocked') == ['borea','greek_borea','primordial_gaia'], '')

print('='*70); print('AF2-N-MONITORING-WINDOW — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
