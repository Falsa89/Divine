#!/usr/bin/env python3
"""
RM1.34 — Boss Family Resistance Table Validator (READ-ONLY)
─────────────────────────────────────────────────────────────────────────
Validates `boss_family_resistance_table_v1.json` against the design
contract sourced from RM1.32-C delta plan. Pure validation, no writes.

Exit 0 = PASS, 1 = FAIL.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
TABLE = ROOT / 'data/design/boss_systems/boss_family_resistance_table_v1.json'
DELTA_PLAN = ROOT / 'data/design/hero_skill_kits/hero_skill_kits_balance_cap_delta_plan_v1.json'
BASELINE_V4 = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132b_v4.json'

REQUIRED_FAMILIES = (
    'story_boss', 'normal_boss', 'elite_boss', 'raid_boss',
    'world_boss', 'event_boss', 'guild_boss',
    'training_dummy', 'pvp_dummy',
)
HARD_CC_KEYS = ('freeze', 'stun', 'silence', 'taunt')
DOT_KEYS = ('burn', 'poison', 'bleed', 'frostbite', 'shock', 'curse')
REQUIRED_POLICY_SECTIONS = (
    'hard_control_policy', 'soft_control_policy', 'dot_policy',
    'anti_heal_policy', 'shield_heal_revive_policy',
    'marchio_boreale_policy', 'domain_policy', 'divine_weapon_synergy_policy',
)
FAMILIES_MARCHIO_CAP_4 = ('raid_boss', 'world_boss', 'guild_boss')
FORBIDDEN_RUNTIME_KEYS_TRUE = ('runtime_attached', 'battle_runtime_attached',
                               'used_by_battle_engine', 'applied_to_combat',
                               'patch_applied_to_catalogs')

failures: list[str] = []
infos: list[str] = []


def fail(sec, msg): failures.append(f'[{sec}] {msg}')
def info(msg): infos.append(msg)


def main() -> int:
    if not TABLE.exists():
        fail('io', f'table missing: {TABLE}')
        return emit()
    try:
        table = json.loads(TABLE.read_text(encoding='utf-8'))
    except Exception as e:
        fail('io', f'JSON parse error: {e}')
        return emit()

    # 1. metadata
    if table.get('task_origin') != 'RM1.34':
        fail('meta', f'task_origin != RM1.34 (got {table.get("task_origin")!r})')
    if table.get('table_id') != 'boss_family_resistance_table_v1':
        fail('meta', 'table_id mismatch')
    md = table.get('metadata') or {}
    for k, v in {
        'design_only': True,
        'runtime_attached': False,
        'battle_runtime_attached': False,
        'used_by_battle_engine': False,
        'db_write': False,
        'balance_values_finalized': False,
        'patch_applied_to_catalogs': False,
        'applied_to_combat': False,
        'no_borea_activation': True,
        'no_borea_visibility_change': True,
        'no_catalog_mutation': True,
    }.items():
        if md.get(k) != v:
            fail('meta', f'metadata.{k}: expected {v!r}, got {md.get(k)!r}')
    if md.get('feature_flag_dependency') != 'SKILL_KIT_RUNTIME_ENABLED':
        fail('meta', 'metadata.feature_flag_dependency != SKILL_KIT_RUNTIME_ENABLED')
    if md.get('feature_flag_currently_enabled') is not False:
        fail('meta', 'metadata.feature_flag_currently_enabled must be false')

    # 2. global policies sanity
    gp = table.get('global_policies') or {}
    marchio = gp.get('marchio_boreale') or {}
    if marchio.get('owner_hero_id') != 'greek_borea':
        fail('global', 'global marchio owner != greek_borea')
    if marchio.get('team_wide_amp_allowed') is not False:
        fail('global', 'global marchio team_wide_amp_allowed != false')
    if marchio.get('boss_default_max_effective_stacks', 99) > 4:
        fail('global', f'global marchio boss_default_max_effective_stacks > 4 (got {marchio.get("boss_default_max_effective_stacks")})')
    domain = gp.get('domain') or {}
    if domain.get('one_domain_active_per_side') is not True:
        fail('global', 'global domain.one_domain_active_per_side != true')
    dw = gp.get('divine_weapon_synergy') or {}
    if dw.get('design_only') is not True or dw.get('runtime_ready') is not False or dw.get('live_numeric_modifier_applied') is not False:
        fail('global', 'global divine_weapon_synergy must be design_only with no live modifier')

    # 3. families
    families = table.get('boss_families') or []
    found_ids = [f.get('family_id') for f in families]
    missing = [r for r in REQUIRED_FAMILIES if r not in found_ids]
    extra = [f for f in found_ids if f not in REQUIRED_FAMILIES]
    if missing:
        fail('families', f'missing families: {missing}')
    if extra:
        fail('families', f'unexpected families: {extra}')
    if not failures or all('families' not in f for f in failures):
        info(f'families present: {len(families)}/{len(REQUIRED_FAMILIES)} ✓')

    for fam in families:
        fid = fam.get('family_id', '?')
        # runtime flags per family
        if fam.get('runtime_attached') is not False:
            fail(fid, 'runtime_attached != false')
        if fam.get('design_only') is not True:
            fail(fid, 'design_only != true')
        # required sections
        for sec in REQUIRED_POLICY_SECTIONS:
            if sec not in fam or not isinstance(fam[sec], dict):
                fail(fid, f'missing/invalid section: {sec}')
        # hard CC keys
        hcp = fam.get('hard_control_policy') or {}
        for k in HARD_CC_KEYS:
            if k not in hcp:
                fail(fid, f'hard_control_policy missing {k}')
            else:
                blk = hcp[k]
                if not isinstance(blk, dict):
                    fail(fid, f'hard_control_policy.{k} not dict')
                    continue
                for req in ('duration_turns_cap', 'chance_multiplier',
                            'diminishing_returns_threshold', 'immune_after_applications'):
                    if req not in blk:
                        fail(fid, f'hard_control_policy.{k}.{req} missing')
        # DoT keys
        dotp = fam.get('dot_policy') or {}
        for k in DOT_KEYS:
            if k not in dotp:
                fail(fid, f'dot_policy missing {k}')
        if dotp.get('can_crit') is not False:
            fail(fid, 'dot_policy.can_crit must be false')
        mdd = dotp.get('max_distinct_dots')
        if not isinstance(mdd, int) or mdd < 1 or mdd > 5:
            fail(fid, f'dot_policy.max_distinct_dots out of safe range: {mdd}')
        tmc = dotp.get('tick_multiplier_cap')
        if not isinstance(tmc, (int, float)) or tmc <= 0 or tmc > 1.0:
            fail(fid, f'dot_policy.tick_multiplier_cap out of range: {tmc}')

        # anti-heal
        ahp = fam.get('anti_heal_policy') or {}
        for req in ('healing_block_max_duration_turns', 'healing_reduction_cap_pct', 'minimum_healing_floor_pct'):
            if req not in ahp:
                fail(fid, f'anti_heal_policy.{req} missing')

        # shield/heal/revive
        shrp = fam.get('shield_heal_revive_policy') or {}
        for req in ('player_heal_effectiveness_pct', 'shield_concurrent_cap_per_ally',
                    'shield_effective_cap_pct', 'revive_per_ally_per_battle_max',
                    'death_protection_max_window_turns'):
            if req not in shrp:
                fail(fid, f'shield_heal_revive_policy.{req} missing')

        # marchio
        mp = fam.get('marchio_boreale_policy') or {}
        if mp.get('owner_hero_id') != 'greek_borea':
            fail(fid, f'marchio owner_hero_id != greek_borea (got {mp.get("owner_hero_id")!r})')
        if mp.get('team_wide_amp_allowed') is not False:
            fail(fid, 'marchio team_wide_amp_allowed != false')
        mes = mp.get('max_effective_stacks')
        if not isinstance(mes, int) or mes < 1:
            fail(fid, f'marchio max_effective_stacks invalid: {mes}')
        if fid in FAMILIES_MARCHIO_CAP_4 and mes > 4:
            fail(fid, f'{fid} marchio max_effective_stacks > 4 (got {mes})')
        if fid == 'pvp_dummy' and mes > 3:
            fail(fid, f'pvp_dummy marchio max_effective_stacks > 3 (got {mes})')

        # domain
        dp = fam.get('domain_policy') or {}
        if dp.get('one_domain_active_per_side') is not True:
            fail(fid, 'domain_policy.one_domain_active_per_side != true')
        if dp.get('strongest_wins') is not True:
            fail(fid, 'domain_policy.strongest_wins != true')
        if dp.get('max_duration_turns', 99) > 3:
            fail(fid, f'domain_policy.max_duration_turns > 3 (got {dp.get("max_duration_turns")})')
        if dp.get('refresh_same_turn_allowed') is not False:
            fail(fid, 'domain_policy.refresh_same_turn_allowed != false')

        # DW synergy
        dwp = fam.get('divine_weapon_synergy_policy') or {}
        if dwp.get('design_only') is not True:
            fail(fid, 'DW synergy design_only != true')
        if dwp.get('live_numeric_modifier_applied') is not False:
            fail(fid, 'DW synergy live_numeric_modifier_applied != false')
        if dwp.get('no_teamwide_global_amp') is not True:
            fail(fid, 'DW synergy no_teamwide_global_amp != true')

        # forbidden true runtime keys at family level
        for key in FORBIDDEN_RUNTIME_KEYS_TRUE:
            if fam.get(key) is True:
                fail(fid, f'{key} == true (forbidden in design-only table)')

    # 4. delta plan still exists
    if not DELTA_PLAN.exists():
        fail('source', 'RM1.32-C delta plan missing')
    else:
        info('RM1.32-C delta plan present ✓')

    # 5. baseline v4 unchanged identity
    if not BASELINE_V4.exists():
        fail('baseline', 'baseline v4 missing')
    else:
        b4 = json.loads(BASELINE_V4.read_text(encoding='utf-8'))
        if b4.get('baseline_id') != 'hero_skill_kit_catalog_baseline_rm132b_v4':
            fail('baseline', 'baseline v4 identity mismatch')
        else:
            info('baseline v4 identity intact ✓')

    return emit()


def emit() -> int:
    if failures:
        print('FAIL: RM1.34 — Boss Family Resistance Table Validator')
        for f in failures:
            print(f'  - {f}')
        if infos:
            for i in infos:
                print(f'  i {i}')
        return 1
    print('PASS: RM1.34 — Boss Family Resistance Table Validator')
    for i in infos:
        print(f'  i {i}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
