#!/usr/bin/env python3
# HOUSING DIMORA DIVINA v2 CANONICAL + SUB-POLICIES VALIDATOR (READ-ONLY)
import json, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
BENCH_DIR = ROOT / 'data/design/benchmark_canonical'
HOUSING_DIR = ROOT / 'data/design/housing'
OUT_DIR = BENCH_DIR
OUT = OUT_DIR / '_sanctuary_housing_dimora_divina_v2_result.json'

V2 = BENCH_DIR / 'sanctuary_housing_dimora_divina_v2.json'
CAP = HOUSING_DIR / 'dimora_divina_room_cap_policy_v1.json'
RES = HOUSING_DIR / 'dimora_divina_resident_bonus_policy_v1.json'
CLM = HOUSING_DIR / 'dimora_divina_resource_claim_policy_v1.json'
VIP = HOUSING_DIR / 'dimora_divina_vip_vault_policy_v1.json'

REQUIRED_ROOMS = {
    'sala_del_trono','armeria','reliquiario','biblioteca_arcana',
    'giardino_sacro','fucina','sala_degli_eroi','tesoreria_stanza_del_tesoro',
}
REQUIRED_CAP_DIMENSIONS = {
    'per_room','per_furniture_category','per_specific_item_or_template',
    'per_bonus_type','per_mode_or_family','master_cap_global',
}
REQUIRED_CAP_FAMILIES = {
    'global_combat','pve_general','boss_titan_behemoth','tower_castle_run',
    'pvp','guild_war_territory','resource_production','affinity_housing_materials_forge_qol',
}

def main():
    errs = []
    # v2 canonical
    if not V2.exists():
        errs.append('v2_canonical_missing')
    else:
        d = json.loads(V2.read_text())
        if d.get('design_only') is not True: errs.append('v2_design_only_not_true')
        if d.get('runtime_implemented') is not False: errs.append('v2_runtime_implemented_not_false')
        if d.get('ui_implemented') is not False: errs.append('v2_ui_implemented_not_false')
        rooms = {r.get('room_id') for r in (d.get('modular_rooms') or [])}
        for r in REQUIRED_ROOMS:
            if r not in rooms: errs.append(f'room_missing:{r}')
        # every room must have min_furniture_slots >= 30
        for r in d.get('modular_rooms') or []:
            if (r.get('min_furniture_slots') or 0) < 30:
                errs.append(f'room_furniture_slots_below_30:{r.get("room_id")}')
        # subscription room is tesoreria
        sub = [r for r in d.get('modular_rooms') or [] if r.get('is_subscription_room')]
        if not sub or sub[0].get('room_id') != 'tesoreria_stanza_del_tesoro':
            errs.append('subscription_room_must_be_tesoreria_stanza_del_tesoro')
        # residents rules
        residents = d.get('residents') or {}
        if residents.get('each_hero_lives_in_only_one_room') is not True: errs.append('residents:one_room_per_hero_missing')
        if residents.get('each_hero_has_unique_resident_bonus') is not True: errs.append('residents:unique_bonus_missing')
        # claim model
        cm = d.get('claim_model') or {}
        if cm.get('centralized_claim_all_required') is not True: errs.append('claim_model:centralized_claim_all_required_missing')
        if cm.get('no_forced_room_by_room_claim') is not True: errs.append('claim_model:no_forced_room_by_room_claim_missing')
        # runtime safety
        rs = d.get('runtime_safety') or {}
        for k, expected in [('battle_runtime_attached',False),('active_bonus_resolver_implemented',False),
                            ('db_write',False),('af2n_unchanged',True),
                            ('borea_visibility_unchanged',True),('primordial_gaia_unchanged_404',True),
                            ('heroes_count_unchanged',100)]:
            if rs.get(k) != expected: errs.append(f'v2_runtime_safety_mismatch:{k}=expected={expected},got={rs.get(k)}')

    # cap policy
    if not CAP.exists():
        errs.append('cap_policy_missing')
    else:
        c = json.loads(CAP.read_text())
        if c.get('design_only') is not True: errs.append('cap_design_only_not_true')
        dims = set(c.get('cap_dimensions') or [])
        for r in REQUIRED_CAP_DIMENSIONS:
            if r not in dims: errs.append(f'cap_dimension_missing:{r}')
        ranges = c.get('directional_cap_ranges_percent') or {}
        for f in REQUIRED_CAP_FAMILIES:
            if f not in ranges: errs.append(f'cap_family_missing:{f}')
        # PvP must be stricter than PvE
        pvp_max = (ranges.get('pvp') or {}).get('max')
        pve_max = (ranges.get('pve_general') or {}).get('max')
        if pvp_max is None or pve_max is None or pvp_max >= pve_max:
            errs.append('pvp_must_be_strict_less_than_pve_general')
        gw_max = (ranges.get('guild_war_territory') or {}).get('max')
        tower_max = (ranges.get('tower_castle_run') or {}).get('max')
        if gw_max is None or tower_max is None or gw_max >= tower_max:
            errs.append('guild_war_must_be_strict_less_than_tower_castle_run')
        # master cap enforced
        mc = c.get('master_cap_global') or {}
        if mc.get('enforced') is not True: errs.append('master_cap_not_enforced')
        if mc.get('prevents_power_creep') is not True: errs.append('master_cap_does_not_prevent_power_creep')
        # decor separate from power
        sep = c.get('separation') or {}
        if sep.get('decorative_capacity_separate_from_power_capacity') is not True:
            errs.append('decor_vs_power_separation_missing')
        # VIP vault contributes to master cap
        vv = c.get('vip_vault_caps') or {}
        if vv.get('vip_vault_secondary_cap_must_be_lower_than_primary_family_cap') is not True:
            errs.append('vip_secondary_cap_constraint_missing')
        if vv.get('master_cap_must_not_be_exceeded_even_with_vip_vault') is not True:
            errs.append('master_cap_with_vip_constraint_missing')

    # resident bonus policy
    if not RES.exists():
        errs.append('resident_bonus_policy_missing')
    else:
        r = json.loads(RES.read_text())
        if r.get('design_only') is not True: errs.append('resident_design_only_not_true')
        ib = r.get('identity_basis') or {}
        if ib.get('is_official_required_for_resident_assignment') is not True:
            errs.append('resident_is_official_required_missing')
        if ib.get('is_legacy_placeholder_or_pending_assets_blocked_from_assignment') is not True:
            errs.append('resident_legacy_or_pending_block_missing')
        rs = r.get('runtime_safety') or {}
        if rs.get('heroes_count_unchanged') != 100:
            errs.append('resident_heroes_count_invariant_missing')

    # resource claim policy
    if not CLM.exists():
        errs.append('resource_claim_policy_missing')
    else:
        cl = json.loads(CLM.read_text())
        if cl.get('design_only') is not True: errs.append('claim_design_only_not_true')
        cm = cl.get('claim_model') or {}
        if cm.get('claim_all_centralized_required') is not True: errs.append('claim_all_centralized_missing')
        if cm.get('claim_all_must_be_idempotent') is not True: errs.append('claim_all_idempotent_missing')
        np = set(cl.get('never_produces') or [])
        for forbidden in ('paid_gem','paid_currency','AF2-N_affinity_gift_credits'):
            if forbidden not in np: errs.append(f'claim_never_produces_missing:{forbidden}')

    # VIP/Vault
    if not VIP.exists():
        errs.append('vip_vault_policy_missing')
    else:
        v = json.loads(VIP.read_text())
        if v.get('design_only') is not True: errs.append('vip_design_only_not_true')
        vr = v.get('vip_rooms') or {}
        if vr.get('secondary_cap_required') is not True: errs.append('vip_secondary_cap_required_missing')
        if vr.get('secondary_cap_lower_than_primary_family_cap') is not True: errs.append('vip_secondary_cap_must_be_lower_missing')
        sr = v.get('subscription_room') or {}
        if sr.get('cannot_unlock_master_cap_bypass') is not True: errs.append('subscription_master_cap_bypass_missing')
        ug = v.get('underground_vault') or {}
        if ug.get('never_circumvents_master_cap') is not True: errs.append('underground_master_cap_circumvent_missing')

    verdict = 'PASS' if not errs else 'FAIL'
    OUT.write_text(json.dumps({'task_origin':'HOUSING-DIMORA-DIVINA-V2','timestamp_utc':datetime.now(timezone.utc).isoformat(),
                               'errors':errs,'verdict':verdict}, indent=2))
    print(f'HOUSING-DIMORA-DIVINA-V2 {verdict} errors={len(errs)}')
    for e in errs: print(' -', e)
    return 0 if verdict=='PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
