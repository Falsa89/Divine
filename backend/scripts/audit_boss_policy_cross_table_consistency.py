#!/usr/bin/env python3
"""
RM1.34-D — Boss Policy Cross-Table Consistency Audit (READ-ONLY)
─────────────────────────────────────────────────────────────────────────────
Audits cross-table consistency across the three approved boss policy tables:
- RM1.34   → boss_family_resistance_table_v1.json
- RM1.34-B → boss_family_element_faction_matrix_v1.json
- RM1.34-C → boss_enrage_phase_policy_table_v1.json

This audit is strictly read-only. It does not modify any source table or
catalog, never writes the DB, and never touches the battle runtime.

It writes a machine-readable report JSON at:
- /app/data/design/boss_systems/boss_policy_cross_table_consistency_report_v1.json

Exit 0 = PASS, 1 = FAIL.
"""
from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/app')
RM134 = ROOT / 'data/design/boss_systems/boss_family_resistance_table_v1.json'
RM134B = ROOT / 'data/design/boss_systems/boss_family_element_faction_matrix_v1.json'
RM134C = ROOT / 'data/design/boss_systems/boss_enrage_phase_policy_table_v1.json'
BASELINE_V4 = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132b_v4.json'
REPORT_OUT = ROOT / 'data/design/boss_systems/boss_policy_cross_table_consistency_report_v1.json'

REQUIRED_FAMILIES = (
    'story_boss', 'normal_boss', 'elite_boss', 'raid_boss',
    'world_boss', 'event_boss', 'guild_boss',
    'training_dummy', 'pvp_dummy',
)
MARCHIO_CAP_HEAVY = ('raid_boss', 'world_boss', 'guild_boss')

# Files that MUST NOT mention the boss policy tables by name/token
RUNTIME_FILES = (
    ROOT / 'backend' / 'battle_engine.py',
    ROOT / 'backend' / 'battle_core.py',
    ROOT / 'frontend' / 'app' / 'combat.tsx',
)
RUNTIME_FORBIDDEN_TOKENS = (
    'boss_family_resistance_table_v1',
    'boss_family_element_faction_matrix_v1',
    'boss_enrage_phase_policy_table_v1',
)

failures: list[str] = []
warnings: list[str] = []
infos: list[str] = []
checks: list[dict] = []


def add_check(name: str, ok: bool, details: str = '', warn_only: bool = False) -> None:
    checks.append({
        'name': name,
        'status': 'PASS' if ok else ('WARN' if warn_only else 'FAIL'),
        'details': details,
    })
    if not ok and not warn_only:
        failures.append(f'[{name}] {details}')
    elif not ok and warn_only:
        warnings.append(f'[{name}] {details}')


def info(msg: str) -> None:
    infos.append(msg)


def load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding='utf-8'))


def family_ids(table: dict, key: str) -> list[str]:
    return [f.get('family_id') for f in (table.get(key) or [])]


def main() -> int:
    # 0. presence
    for f in (RM134, RM134B, RM134C):
        if not f.exists():
            failures.append(f'[io] source missing: {f}')
            return emit(audit_result='FAIL', t134={}, t134b={}, t134c={})

    t134 = load_json(RM134)
    t134b = load_json(RM134B)
    t134c = load_json(RM134C)

    # 1. design-only metadata in all three
    for name, t, fam_key in (
        ('RM1.34', t134, 'boss_families'),
        ('RM1.34-B', t134b, 'boss_families'),
        ('RM1.34-C', t134c, 'boss_families'),
    ):
        md = t.get('metadata') or {}
        ok = (
            md.get('design_only') is True
            and md.get('runtime_attached') is False
            and md.get('battle_runtime_attached') is False
            and md.get('used_by_battle_engine') is False
        )
        add_check(f'metadata.design_only_inert[{name}]', ok,
                  'design_only=true, runtime_attached=false, battle_runtime_attached=false, used_by_battle_engine=false'
                  if ok else f'metadata flags incorrect in {name}')
        # no_borea_activation when present
        if 'no_borea_activation' in md:
            add_check(f'metadata.no_borea_activation[{name}]', md.get('no_borea_activation') is True,
                      'no_borea_activation=true' if md.get('no_borea_activation') is True
                      else f'{name}.metadata.no_borea_activation must be true')

    # 2. boss family IDs identical across 3 tables
    f134 = family_ids(t134, 'boss_families')
    f134b = family_ids(t134b, 'boss_families')
    f134c = family_ids(t134c, 'boss_families')
    set_expected = set(REQUIRED_FAMILIES)
    sets_equal = (set(f134) == set_expected and set(f134b) == set_expected and set(f134c) == set_expected)
    add_check('families_match.9x3', sets_equal,
              f'families: RM1.34={len(f134)}, RM1.34-B={len(f134b)}, RM1.34-C={len(f134c)}, set-equal-to-required={sets_equal}'
              if sets_equal else f'family sets differ: RM1.34={sorted(f134)} RM1.34-B={sorted(f134b)} RM1.34-C={sorted(f134c)}')

    # build per-family dicts indexed by family_id
    by134 = {f['family_id']: f for f in t134.get('boss_families') or []}
    by134b = {f['family_id']: f for f in t134b.get('boss_families') or []}
    by134c = {f['family_id']: f for f in t134c.get('boss_families') or []}

    # 3. Marchio consistency
    marchio_owner_ok = True
    marchio_amp_ok = True
    marchio_phase_no_activation_ok = True
    marchio_cap_heavy_ok = True
    marchio_cap_pvp_ok = True
    details_marchio: list[str] = []
    for fid in REQUIRED_FAMILIES:
        # RM1.34 table per-family policy
        rm134_marchio = (by134.get(fid) or {}).get('marchio_boreale_policy') or {}
        if rm134_marchio:
            if rm134_marchio.get('owner_hero_id') != 'greek_borea':
                marchio_owner_ok = False
                details_marchio.append(f'{fid}/RM1.34 owner!=greek_borea ({rm134_marchio.get("owner_hero_id")!r})')
            if rm134_marchio.get('team_wide_amp_allowed') is not False:
                marchio_amp_ok = False
                details_marchio.append(f'{fid}/RM1.34 team_wide_amp_allowed!=false')
            cap = rm134_marchio.get('max_effective_stacks')
            if cap is not None:
                if fid in MARCHIO_CAP_HEAVY and cap > 4:
                    marchio_cap_heavy_ok = False
                    details_marchio.append(f'{fid}/RM1.34 cap {cap} > 4')
                if fid == 'pvp_dummy' and cap > 3:
                    marchio_cap_pvp_ok = False
                    details_marchio.append(f'{fid}/RM1.34 pvp cap {cap} > 3')
        # RM1.34-B matrix per-family special_cases
        rm134b_marchio = ((by134b.get(fid) or {}).get('special_cases') or {}).get('marchio_boreale') or {}
        if rm134b_marchio:
            if rm134b_marchio.get('owner_hero_id') != 'greek_borea':
                marchio_owner_ok = False
                details_marchio.append(f'{fid}/RM1.34-B owner!=greek_borea')
            if rm134b_marchio.get('team_wide_amp_allowed') is not False:
                marchio_amp_ok = False
                details_marchio.append(f'{fid}/RM1.34-B team_wide_amp_allowed!=false')
            cap = rm134b_marchio.get('max_effective_stacks_in_this_family')
            if cap is not None:
                if fid in MARCHIO_CAP_HEAVY and cap > 4:
                    marchio_cap_heavy_ok = False
                    details_marchio.append(f'{fid}/RM1.34-B cap {cap} > 4')
                if fid == 'pvp_dummy' and cap > 3:
                    marchio_cap_pvp_ok = False
                    details_marchio.append(f'{fid}/RM1.34-B pvp cap {cap} > 3')
        # RM1.34-C phase policy
        rm134c_marchio = (by134c.get(fid) or {}).get('marchio_boreale_phase_policy') or {}
        if rm134c_marchio:
            if rm134c_marchio.get('owner_hero_id') != 'greek_borea':
                marchio_owner_ok = False
                details_marchio.append(f'{fid}/RM1.34-C owner!=greek_borea')
            if rm134c_marchio.get('team_wide_amp_allowed') is not False:
                marchio_amp_ok = False
                details_marchio.append(f'{fid}/RM1.34-C team_wide_amp_allowed!=false')
            if rm134c_marchio.get('no_activation') is not True:
                marchio_phase_no_activation_ok = False
                details_marchio.append(f'{fid}/RM1.34-C no_activation!=true')
            msbp = rm134c_marchio.get('max_stacks_by_phase') or []
            if msbp:
                m = max(msbp)
                if fid in MARCHIO_CAP_HEAVY and m > 4:
                    marchio_cap_heavy_ok = False
                    details_marchio.append(f'{fid}/RM1.34-C max(stacks)={m} > 4')
                if fid == 'pvp_dummy' and m > 3:
                    marchio_cap_pvp_ok = False
                    details_marchio.append(f'{fid}/RM1.34-C pvp max(stacks)={m} > 3')
    add_check('marchio.owner_greek_borea', marchio_owner_ok,
              'all marchio owner_hero_id=greek_borea' if marchio_owner_ok else '; '.join(details_marchio))
    add_check('marchio.team_wide_amp_disallowed', marchio_amp_ok,
              'team_wide_amp_allowed=false everywhere' if marchio_amp_ok else '; '.join(details_marchio))
    add_check('marchio.phase_no_activation', marchio_phase_no_activation_ok,
              'phase policy no_activation=true everywhere' if marchio_phase_no_activation_ok else '; '.join(details_marchio))
    add_check('marchio.cap_heavy_le_4', marchio_cap_heavy_ok,
              'raid/world/guild marchio cap <= 4' if marchio_cap_heavy_ok else '; '.join(details_marchio))
    add_check('marchio.cap_pvp_le_3', marchio_cap_pvp_ok,
              'pvp_dummy marchio cap <= 3' if marchio_cap_pvp_ok else '; '.join(details_marchio))

    # 4. Domain consistency
    domain_ok = True
    domain_details: list[str] = []
    # RM1.34: domain_policy lives PER-FAMILY (not top-level)
    for fid in REQUIRED_FAMILIES:
        rm134_dom = (by134.get(fid) or {}).get('domain_policy') or {}
        if not rm134_dom:
            continue
        if rm134_dom.get('one_domain_active_per_side') is not True:
            domain_ok = False
            domain_details.append(f'{fid}/RM1.34.domain.one_domain_active_per_side!=true')
        if rm134_dom.get('strongest_wins') is not True:
            domain_ok = False
            domain_details.append(f'{fid}/RM1.34.domain.strongest_wins!=true')
        if rm134_dom.get('max_duration_turns') is not None and rm134_dom.get('max_duration_turns') > 3:
            domain_ok = False
            domain_details.append(f"{fid}/RM1.34.domain.max_duration_turns={rm134_dom.get('max_duration_turns')} > 3")
    # RM1.34-B: per family special_cases.domain_effect
    for fid in REQUIRED_FAMILIES:
        de = ((by134b.get(fid) or {}).get('special_cases') or {}).get('domain_effect') or {}
        if de:
            if de.get('design_only') is not True:
                domain_ok = False
                domain_details.append(f'{fid}/RM1.34-B domain.design_only!=true')
            if de.get('runtime_ready') is not False:
                domain_ok = False
                domain_details.append(f'{fid}/RM1.34-B domain.runtime_ready!=false')
            if de.get('max_duration_turns') is not None and de.get('max_duration_turns') > 3:
                domain_ok = False
                domain_details.append(f'{fid}/RM1.34-B domain.max_duration_turns>{3}')
    # RM1.34-C: per family domain_phase_policy
    for fid in REQUIRED_FAMILIES:
        dp = (by134c.get(fid) or {}).get('domain_phase_policy') or {}
        if dp.get('one_domain_active_per_side') is not True:
            domain_ok = False
            domain_details.append(f'{fid}/RM1.34-C domain.one_domain_active_per_side!=true')
        if dp.get('strongest_wins') is not True:
            domain_ok = False
            domain_details.append(f'{fid}/RM1.34-C domain.strongest_wins!=true')
        if dp.get('no_same_turn_refresh') is not True:
            domain_ok = False
            domain_details.append(f'{fid}/RM1.34-C domain.no_same_turn_refresh!=true')
        if dp.get('max_duration_turns') is not None and dp.get('max_duration_turns') > 3:
            domain_ok = False
            domain_details.append(f"{fid}/RM1.34-C domain.max_duration_turns={dp.get('max_duration_turns')} > 3")
    add_check('domain.consistent', domain_ok,
              'domain rules consistent across 3 tables (one_active_per_side, strongest_wins, no_same_turn_refresh, max_duration<=3)'
              if domain_ok else '; '.join(domain_details))

    # 5. Divine Weapon synergy consistency
    dw_ok = True
    dw_details: list[str] = []
    # RM1.34: divine_weapon_synergy_policy lives PER-FAMILY (not top-level)
    for fid in REQUIRED_FAMILIES:
        rm134_dw = (by134.get(fid) or {}).get('divine_weapon_synergy_policy') or {}
        if not rm134_dw:
            continue
        if rm134_dw.get('design_only') is not True:
            dw_ok = False
            dw_details.append(f'{fid}/RM1.34.dw.design_only!=true')
        if rm134_dw.get('live_numeric_modifier_applied') is not False:
            dw_ok = False
            dw_details.append(f'{fid}/RM1.34.dw.live_numeric_modifier_applied!=false')
        cap = rm134_dw.get('numeric_modifier_cap_future_pct')
        if cap is not None and cap > 10:
            dw_ok = False
            dw_details.append(f'{fid}/RM1.34.dw global cap {cap}% > 10%')
        cap_pvp = rm134_dw.get('pvp_modifier_cap_future_pct')
        if cap_pvp is not None and cap_pvp > 5:
            dw_ok = False
            dw_details.append(f'{fid}/RM1.34.dw pvp cap {cap_pvp}% > 5%')
    for fid in REQUIRED_FAMILIES:
        # RM1.34-B
        dwb = ((by134b.get(fid) or {}).get('special_cases') or {}).get('divine_weapon_synergy') or {}
        if dwb:
            if dwb.get('design_only') is not True:
                dw_ok = False
                dw_details.append(f'{fid}/RM1.34-B dw.design_only!=true')
            if dwb.get('live_numeric_modifier_applied') is not False:
                dw_ok = False
                dw_details.append(f'{fid}/RM1.34-B dw.live_numeric_modifier_applied!=false')
            if dwb.get('per_owner_only') is not True:
                dw_ok = False
                dw_details.append(f'{fid}/RM1.34-B dw.per_owner_only!=true')
            if dwb.get('no_teamwide_global_amp') is not True:
                dw_ok = False
                dw_details.append(f'{fid}/RM1.34-B dw.no_teamwide_global_amp!=true')
            if dwb.get('numeric_modifier_cap_future_pct') is not None and dwb.get('numeric_modifier_cap_future_pct') > 10:
                dw_ok = False
                dw_details.append(f"{fid}/RM1.34-B dw cap {dwb.get('numeric_modifier_cap_future_pct')}%>10%")
            if dwb.get('pvp_modifier_cap_future_pct') is not None and dwb.get('pvp_modifier_cap_future_pct') > 5:
                dw_ok = False
                dw_details.append(f"{fid}/RM1.34-B dw pvp cap {dwb.get('pvp_modifier_cap_future_pct')}%>5%")
        # RM1.34-C
        dwc = (by134c.get(fid) or {}).get('divine_weapon_phase_policy') or {}
        if dwc:
            if dwc.get('design_only') is not True:
                dw_ok = False
                dw_details.append(f'{fid}/RM1.34-C dw.design_only!=true')
            if dwc.get('live_numeric_modifier_applied') is not False:
                dw_ok = False
                dw_details.append(f'{fid}/RM1.34-C dw.live_numeric_modifier_applied!=false')
            if dwc.get('per_owner_only') is not True:
                dw_ok = False
                dw_details.append(f'{fid}/RM1.34-C dw.per_owner_only!=true')
            if dwc.get('no_teamwide_global_amp') is not True:
                dw_ok = False
                dw_details.append(f'{fid}/RM1.34-C dw.no_teamwide_global_amp!=true')
            if dwc.get('enrage_modifier_cap_future_pct') is not None and dwc.get('enrage_modifier_cap_future_pct') > 10:
                dw_ok = False
                dw_details.append(f"{fid}/RM1.34-C dw enrage cap {dwc.get('enrage_modifier_cap_future_pct')}%>10%")
            if dwc.get('pvp_modifier_cap_future_pct') is not None and dwc.get('pvp_modifier_cap_future_pct') > 5:
                dw_ok = False
                dw_details.append(f"{fid}/RM1.34-C dw pvp cap {dwc.get('pvp_modifier_cap_future_pct')}%>5%")
    add_check('divine_weapon.consistent', dw_ok,
              'DW synergy: design_only=true, live_numeric=false, per_owner_only=true, caps <=10/5%' if dw_ok else '; '.join(dw_details))

    # 6. training_dummy consistency
    td_ok = True
    td_details: list[str] = []
    # RM1.34-B matrix should be near-neutral
    td_matrix = by134b.get('training_dummy') or {}
    for k in ('element_resistance_modifiers', 'faction_resistance_modifiers'):
        rows = td_matrix.get(k) or {}
        for axis, row in rows.items():
            for fld in ('damage_taken_multiplier', 'status_chance_multiplier', 'dot_tick_multiplier'):
                if fld in row:
                    v = row.get(fld)
                    if v is None: continue
                    if not (0.95 <= float(v) <= 1.05 + 1e-9):
                        td_ok = False
                        td_details.append(f'RM1.34-B training_dummy.{k}.{axis}.{fld}={v} not in [0.95,1.05]')
    # RM1.34-C: enrage disabled
    td_phase = by134c.get('training_dummy') or {}
    if (td_phase.get('enrage_policy') or {}).get('enabled') is not False:
        td_ok = False
        td_details.append('RM1.34-C training_dummy enrage not disabled')
    if (td_phase.get('phase_model') or {}).get('phase_count') != 1:
        td_ok = False
        td_details.append('RM1.34-C training_dummy phase_count!=1')
    # RM1.34 family policy (training_dummy minimal resistance)
    td_134 = by134.get('training_dummy') or {}
    if td_134:
        # No hard immunities expected to be true (only design tags)
        hc = (td_134.get('hard_control_policy') or {})
        for k, v in hc.items():
            if k.endswith('_immunity') and v is True:
                td_ok = False
                td_details.append(f'RM1.34 training_dummy.{k}=true (hard immunity not expected)')
    add_check('training_dummy.consistent', td_ok,
              'training_dummy neutral matrix + enrage disabled + phase=1 + no hard immunities' if td_ok else '; '.join(td_details))

    # 7. pvp_dummy consistency
    pv_ok = True
    pv_details: list[str] = []
    pv_matrix = by134b.get('pvp_dummy') or {}
    for k in ('element_resistance_modifiers', 'faction_resistance_modifiers'):
        rows = pv_matrix.get(k) or {}
        for axis, row in rows.items():
            for fld in ('damage_taken_multiplier', 'status_chance_multiplier', 'dot_tick_multiplier'):
                if fld in row:
                    v = row.get(fld)
                    if v is None: continue
                    if not (0.95 <= float(v) <= 1.05 + 1e-9):
                        pv_ok = False
                        pv_details.append(f'RM1.34-B pvp_dummy.{k}.{axis}.{fld}={v} not in [0.95,1.05]')
    pv_phase = by134c.get('pvp_dummy') or {}
    ep = pv_phase.get('enrage_policy') or {}
    if ep.get('enabled') is not False and not ep.get('pvp_test_only', False):
        pv_ok = False
        pv_details.append('RM1.34-C pvp_dummy enrage neither disabled nor pvp_test_only')
    al = pv_phase.get('anti_loop_policy') or {}
    if al.get('hard_control_chain_limit') is not None and al['hard_control_chain_limit'] > 2:
        pv_ok = False
        pv_details.append(f"RM1.34-C pvp_dummy hard_control_chain_limit={al['hard_control_chain_limit']} > 2")
    # status chance: must be PvP-safe (we accept neutral band)
    sc_caps = ep.get('status_chance_multiplier_cap')
    if sc_caps is not None and float(sc_caps) > 1.05 + 1e-9:
        pv_ok = False
        pv_details.append(f'RM1.34-C pvp_dummy status_chance_multiplier_cap={sc_caps} > 1.05')
    add_check('pvp_dummy.consistent', pv_ok,
              'pvp_dummy PvP-safe neutral matrix + enrage disabled-or-pvp_test_only + hard_control_chain<=2' if pv_ok else '; '.join(pv_details))

    # 8. raid/world/guild consistency (broad)
    rwg_ok = True
    rwg_details: list[str] = []
    caps_world = ((by134c.get('world_boss') or {}).get('enrage_policy') or {})
    caps_raid = ((by134c.get('raid_boss') or {}).get('enrage_policy') or {})
    caps_guild = ((by134c.get('guild_boss') or {}).get('enrage_policy') or {})
    al_world = ((by134c.get('world_boss') or {}).get('anti_loop_policy') or {})
    al_raid = ((by134c.get('raid_boss') or {}).get('anti_loop_policy') or {})
    al_guild = ((by134c.get('guild_boss') or {}).get('anti_loop_policy') or {})
    # Marchio caps everywhere <= 4 already checked above. Damage cap <= family ceiling already in validator.
    # broad rule: world heal cap <= raid heal cap AND world heal cap <= guild heal cap
    if not (float(al_world.get('healing_effectiveness_cap', 1)) <= float(al_raid.get('healing_effectiveness_cap', 1)) + 1e-9
            and float(al_world.get('healing_effectiveness_cap', 1)) <= float(al_guild.get('healing_effectiveness_cap', 1)) + 1e-9):
        rwg_ok = False
        rwg_details.append(f"world heal cap {al_world.get('healing_effectiveness_cap')} not <= raid {al_raid.get('healing_effectiveness_cap')} / guild {al_guild.get('healing_effectiveness_cap')}")
    # broad rule: hard control chain limit world <= raid and world <= guild
    if not (int(al_world.get('hard_control_chain_limit', 99)) <= int(al_raid.get('hard_control_chain_limit', 99))
            and int(al_world.get('hard_control_chain_limit', 99)) <= int(al_guild.get('hard_control_chain_limit', 99))):
        rwg_ok = False
        rwg_details.append(f"world hard_control_chain_limit {al_world.get('hard_control_chain_limit')} not <= raid/guild")
    # broad rule: DoT stack limit world <= raid and world <= guild
    if not (int(al_world.get('dot_stack_limit', 99)) <= int(al_raid.get('dot_stack_limit', 99))
            and int(al_world.get('dot_stack_limit', 99)) <= int(al_guild.get('dot_stack_limit', 99))):
        rwg_ok = False
        rwg_details.append(f"world dot_stack_limit {al_world.get('dot_stack_limit')} not <= raid/guild")
    # broad rule: shield refresh world <= raid <= guild loose ordering
    if not (int(al_world.get('shield_refresh_limit', 99)) <= int(al_raid.get('shield_refresh_limit', 99))
            and int(al_world.get('shield_refresh_limit', 99)) <= int(al_guild.get('shield_refresh_limit', 99))):
        rwg_ok = False
        rwg_details.append(f"world shield_refresh_limit not <= raid/guild")
    # no hard counter multipliers beyond safe bounds: matrix damage_taken_multiplier in [0.70,1.30]
    for fid in ('raid_boss', 'world_boss', 'guild_boss'):
        ems = (by134b.get(fid) or {}).get('element_resistance_modifiers') or {}
        for el, row in ems.items():
            v = row.get('damage_taken_multiplier')
            if v is None: continue
            if not (0.70 <= float(v) <= 1.30 + 1e-9):
                rwg_ok = False
                rwg_details.append(f'{fid}/matrix element.{el} dtm={v} out of [0.70,1.30]')
    add_check('raid_world_guild.consistent', rwg_ok,
              'raid/world/guild caps consistent (world ≤ raid/guild on anti-loop, no hard counter outside [0.70,1.30])' if rwg_ok else '; '.join(rwg_details))

    # 9. Baseline consistency
    baseline_ok = True
    baseline_details: list[str] = []
    if not BASELINE_V4.exists():
        baseline_ok = False
        baseline_details.append(f'baseline v4 file missing: {BASELINE_V4}')
    else:
        info(f'baseline v4 anchor present: {BASELINE_V4.name}')
    for name, t in (('RM1.34', t134), ('RM1.34-B', t134b), ('RM1.34-C', t134c)):
        md = t.get('metadata') or {}
        # RM1.34 keeps anchor at top-level; RM1.34-B/C keep it in metadata.
        anchor = md.get('baseline_anchor_at_creation') or t.get('baseline_anchor_at_creation')
        if anchor != 'hero_skill_kit_catalog_baseline_rm132b_v4':
            baseline_ok = False
            baseline_details.append(f'{name}.baseline_anchor_at_creation={anchor!r}')
    add_check('baseline_v4.consistent', baseline_ok,
              'all tables anchored at baseline_v4 and baseline file present' if baseline_ok else '; '.join(baseline_details))

    # 10. Runtime isolation: grep runtime files for boss policy filenames/tokens
    iso_ok = True
    iso_details: list[str] = []
    for f in RUNTIME_FILES:
        if not f.exists():
            iso_details.append(f'runtime file not found (acceptable for audit): {f}')
            continue
        try:
            text = f.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            iso_ok = False
            iso_details.append(f'{f}: read error {e}')
            continue
        for tok in RUNTIME_FORBIDDEN_TOKENS:
            if tok in text:
                iso_ok = False
                iso_details.append(f'{f.name} mentions forbidden token {tok!r}')
    add_check('runtime_isolation.confirmed', iso_ok,
              'no runtime file references any boss policy table' if iso_ok else '; '.join(iso_details))

    # 11. source tables NOT modified (sanity: design_only=true, task_origin correct, runtime_attached false)
    src_ok = True
    src_details: list[str] = []
    expected_origin = {RM134: 'RM1.34', RM134B: 'RM1.34-B', RM134C: 'RM1.34-C'}
    for p, t in ((RM134, t134), (RM134B, t134b), (RM134C, t134c)):
        if t.get('task_origin') != expected_origin[p]:
            src_ok = False
            src_details.append(f'{p.name}.task_origin={t.get("task_origin")!r} expected {expected_origin[p]!r}')
        md = t.get('metadata') or {}
        if md.get('design_only') is not True:
            src_ok = False
            src_details.append(f'{p.name}.metadata.design_only must be true')
        if md.get('runtime_attached') is not False:
            src_ok = False
            src_details.append(f'{p.name}.metadata.runtime_attached must be false')
    add_check('source_tables.unmodified_inert', src_ok,
              '3 source tables retain design_only=true, runtime_attached=false, correct task_origin' if src_ok else '; '.join(src_details))

    # Compose report and write JSON
    audit_result = 'PASS' if not failures else 'FAIL'
    report = {
        'report_id': 'boss_policy_cross_table_consistency_report_v1',
        'task_origin': 'RM1.34-D',
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'source_tables': [
            'boss_family_resistance_table_v1',
            'boss_family_element_faction_matrix_v1',
            'boss_enrage_phase_policy_table_v1',
        ],
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm132b_v4',
        'design_only': True,
        'runtime_attached': False,
        'no_runtime_activation': True,
        'no_db_write': True,
        'no_catalog_mutation': True,
        'audit_result': audit_result,
        'family_count': 9,
        'family_ids': list(REQUIRED_FAMILIES),
        'checks_summary': {
            'families_match': all(c['status'] == 'PASS' for c in checks if c['name'].startswith('families_match')),
            'marchio_consistent': all(c['status'] == 'PASS' for c in checks if c['name'].startswith('marchio.')),
            'domain_consistent': all(c['status'] == 'PASS' for c in checks if c['name'].startswith('domain.')),
            'divine_weapon_consistent': all(c['status'] == 'PASS' for c in checks if c['name'].startswith('divine_weapon.')),
            'training_dummy_consistent': all(c['status'] == 'PASS' for c in checks if c['name'].startswith('training_dummy.')),
            'pvp_dummy_consistent': all(c['status'] == 'PASS' for c in checks if c['name'].startswith('pvp_dummy.')),
            'raid_world_guild_consistent': all(c['status'] == 'PASS' for c in checks if c['name'].startswith('raid_world_guild.')),
            'baseline_v4_consistent': all(c['status'] == 'PASS' for c in checks if c['name'].startswith('baseline_v4.')),
            'runtime_isolation_confirmed': all(c['status'] == 'PASS' for c in checks if c['name'].startswith('runtime_isolation.')),
            'source_tables_unmodified': all(c['status'] == 'PASS' for c in checks if c['name'].startswith('source_tables.')),
        },
        'checks': checks,
        'warnings': warnings,
        'failures': failures,
        'next_recommendations': [
            'Hold all 3 boss policy tables design-only until runtime adapter activation.',
            'Re-run this audit any time any of the 3 source tables changes.',
            'When boss runtime is unlocked, require the audit to PASS as a gating step.',
        ],
    }
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    return emit(audit_result=audit_result, t134=t134, t134b=t134b, t134c=t134c)


def emit(audit_result: str, t134: dict, t134b: dict, t134c: dict) -> int:
    print('=' * 72)
    print('RM1.34-D Boss Policy Cross-Table Consistency Audit')
    print('=' * 72)
    for i in infos: print(f'INFO: {i}')
    for c in checks:
        print(f'  {c["status"]:4s}  {c["name"]:42s}  {c["details"][:200]}')
    for w in warnings: print(f'WARN: {w}')
    if failures:
        print(f'\nFAILURES ({len(failures)}):')
        for f in failures: print(f'  - {f}')
    print(f'\nReport: {REPORT_OUT}')
    print(f'\nRESULT: {audit_result}')
    return 0 if audit_result == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
