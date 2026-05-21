#!/usr/bin/env python3
"""COSMETIC-A: Validate policy files (read-only)."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path
OUT = Path('/app/data/design/cosmetics/_validate_cosmetic_system_policy_v1_result.json')
ROOT = Path('/app/data/design/cosmetics')
FILES = [
    'cosmetic_system_policy_v1.json',
    'cosmetic_rarity_bonus_table_v1.json',
    'cosmetic_power_cap_policy_v1.json',
    'cosmetic_account_server_scope_policy_v1.json',
    'cosmetic_source_and_rerun_policy_v1.json',
]
RARITIES = ['common','rare','epic','legendary','mythic','divine']


def main():
    errs=[]; data={}
    for fn in FILES:
        p=ROOT/fn
        if not p.exists(): errs.append(f'missing:{fn}'); continue
        try: data[fn]=json.loads(p.read_text())
        except Exception as e: errs.append(f'parse:{fn}:{e}')
    # Policy invariants
    sys_pol = data.get('cosmetic_system_policy_v1.json', {})
    if not sys_pol.get('design_only'): errs.append('policy:not_design_only')
    if sys_pol.get('runtime_attached'): errs.append('policy:runtime_attached')
    if sys_pol.get('battle_runtime_attached'): errs.append('policy:battle_attached')
    if (sys_pol.get('global_rules') or {}).get('equipped_title_limit') != 1: errs.append('policy:equip_title_limit!=1')
    if (sys_pol.get('global_rules') or {}).get('skin_bonus_scope') != 'hero_bound': errs.append('policy:skin_scope_wrong')
    # Rarity table
    rar = data.get('cosmetic_rarity_bonus_table_v1.json', {})
    for r in RARITIES:
        if r not in (rar.get('rarities') or {}): errs.append(f'rarity:missing:{r}')
        if r not in (rar.get('title_bonus_ranges_design_caps') or {}): errs.append(f'title_range:missing:{r}')
        if r not in (rar.get('skin_bonus_ranges_design_caps') or {}): errs.append(f'skin_range:missing:{r}')
    # Power caps
    cap = data.get('cosmetic_power_cap_policy_v1.json', {})
    g = cap.get('global_caps_by_mode') or {}
    pve_max = g.get('pve', {}).get('total_cosmetic_power_pct_max', -1)
    pvp_max = g.get('pvp', {}).get('total_cosmetic_power_pct_max', -1)
    gw_max  = g.get('guild_war', {}).get('total_cosmetic_power_pct_max', -1)
    boss_max= g.get('boss', {}).get('total_cosmetic_power_pct_max', -1)
    if pve_max > 15.0: errs.append(f'pve_cap_too_high:{pve_max}')
    if pvp_max > 8.0:  errs.append(f'pvp_cap_too_high:{pvp_max}')
    if gw_max > 8.0:   errs.append(f'gw_cap_too_high:{gw_max}')
    if boss_max > 10.0:errs.append(f'boss_cap_too_high:{boss_max}')
    if not (pvp_max < pve_max): errs.append('pvp_not_stricter_than_pve')
    if not (gw_max <= pvp_max): errs.append('gw_not_aligned_with_pvp')
    ir = (cap.get('flat_stat_caps') or {}).get('initial_rage_flat') or {}
    if ir.get('pve_max') != 20 or ir.get('pvp_max') != 10: errs.append(f'initial_rage_caps_wrong:{ir}')
    sp = (cap.get('flat_stat_caps') or {}).get('speed_flat') or {}
    if sp.get('pve_max') != 10 or sp.get('pvp_max') != 5: errs.append(f'speed_caps_wrong:{sp}')
    if not cap.get('pvp_stricter_than_pve_invariant'): errs.append('pvp_stricter_invariant_missing')
    # Scope
    scope = data.get('cosmetic_account_server_scope_policy_v1.json', {})
    rules = scope.get('scope_rules') or {}
    if 'account_wide' not in rules or 'server_bound' not in rules: errs.append('scope:missing_rule')
    # Source/Rerun
    src = data.get('cosmetic_source_and_rerun_policy_v1.json', {})
    if 'server_first' not in (src.get('source_types') or {}): errs.append('source:server_first_missing')
    if (src.get('source_types') or {}).get('server_first', {}).get('rerun_eligible') is True:
        errs.append('source:server_first_must_not_rerun')

    out = {
        'task_origin':'COSMETIC-A-VALIDATE-POLICY',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'files_checked': FILES,
        'errors': errs,
        'verdict': 'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out,indent=2,default=str))
    print(f"verdict={out['verdict']} errors={len(errs)}")
    for e in errs: print(f'  - {e}')
    return 0 if not errs else 2


if __name__ == '__main__': sys.exit(main())
