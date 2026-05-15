#!/usr/bin/env python3
"""
RM1.34-C — Boss Enrage / Phase Transition Policy Table Validator (READ-ONLY)
─────────────────────────────────────────────────────────────────────────────
Validates `boss_enrage_phase_policy_table_v1.json`.

Exit 0 = PASS, 1 = FAIL.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
TABLE = ROOT / 'data/design/boss_systems/boss_enrage_phase_policy_table_v1.json'
RM134 = ROOT / 'data/design/boss_systems/boss_family_resistance_table_v1.json'
RM134B = ROOT / 'data/design/boss_systems/boss_family_element_faction_matrix_v1.json'
BASELINE_V4 = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132b_v4.json'

REQUIRED_FAMILIES = (
    'story_boss', 'normal_boss', 'elite_boss', 'raid_boss',
    'world_boss', 'event_boss', 'guild_boss',
    'training_dummy', 'pvp_dummy',
)

# Safe damage_multiplier_cap ceilings per family (prompt rules)
DMG_CAP_BY_FAMILY = {
    'story_boss': 1.20, 'normal_boss': 1.20,
    'elite_boss': 1.30, 'event_boss': 1.30,
    'raid_boss': 1.40, 'guild_boss': 1.40,
    'world_boss': 1.50,
    'training_dummy': 1.00, 'pvp_dummy': 1.05,
}
ALLOWED_TRIGGER_TYPES = {'hp_threshold', 'turn_count', 'soft_timer', 'failed_mechanic', 'none'}
ALLOWED_TRANSITION_BEHAVIORS = {'preserve', 'decay', 'cleanse', 'cap'}

FORBIDDEN_RUNTIME_KEYS_TRUE = (
    'runtime_attached', 'battle_runtime_attached',
    'used_by_battle_engine', 'applied_to_combat',
    'patch_applied_to_catalogs', 'db_write',
)
FORBIDDEN_DB_WRITE_HINTS = ('db_write_active', 'mongo_write', 'sql_insert', 'persistence_active')

failures: list[str] = []
warnings: list[str] = []
infos: list[str] = []


def fail(sec: str, msg: str) -> None: failures.append(f'[{sec}] {msg}')
def warn(sec: str, msg: str) -> None: warnings.append(f'[{sec}] {msg}')
def info(msg: str) -> None: infos.append(msg)


def check_no_true_runtime_flags(obj, path: str) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in FORBIDDEN_RUNTIME_KEYS_TRUE and v is True:
                fail('runtime', f'{path}.{k}=True forbidden')
            if isinstance(v, (dict, list)):
                check_no_true_runtime_flags(v, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            check_no_true_runtime_flags(item, f'{path}[{i}]')


def check_no_db_hints(obj, path: str) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in FORBIDDEN_DB_WRITE_HINTS:
                fail('db', f'{path}.{k} forbidden db-write hint')
            if isinstance(v, (dict, list)):
                check_no_db_hints(v, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            check_no_db_hints(item, f'{path}[{i}]')


def main() -> int:
    if not TABLE.exists():
        fail('io', f'table file missing: {TABLE}')
        return emit()
    try:
        data = json.loads(TABLE.read_text(encoding='utf-8'))
    except Exception as e:
        fail('io', f'JSON parse error: {e}')
        return emit()

    # 1. identity & metadata
    if data.get('table_id') != 'boss_enrage_phase_policy_table_v1':
        fail('meta', f"table_id mismatch (got {data.get('table_id')!r})")
    if data.get('task_origin') != 'RM1.34-C':
        fail('meta', f"task_origin != RM1.34-C (got {data.get('task_origin')!r})")
    sources = data.get('source_tables') or []
    for req in ('boss_family_resistance_table_v1', 'boss_family_element_faction_matrix_v1'):
        if req not in sources:
            fail('meta', f'source_tables missing {req}')
    md = data.get('metadata') or {}
    for key, want in (('design_only', True), ('runtime_attached', False),
                      ('battle_runtime_attached', False), ('used_by_battle_engine', False),
                      ('db_write', False), ('patch_applied_to_catalogs', False),
                      ('no_borea_activation', True), ('feature_flag_currently_enabled', False)):
        if md.get(key) is not want:
            fail('meta', f'metadata.{key} must be {want}')
    if md.get('feature_flag_dependency') != 'SKILL_KIT_RUNTIME_ENABLED':
        fail('meta', 'metadata.feature_flag_dependency must be SKILL_KIT_RUNTIME_ENABLED')
    if md.get('baseline_anchor_at_creation') != 'hero_skill_kit_catalog_baseline_rm132b_v4':
        fail('meta', 'metadata.baseline_anchor_at_creation must be hero_skill_kit_catalog_baseline_rm132b_v4')

    # 2. families presence and shape
    families = data.get('boss_families') or []
    if len(families) != 9:
        fail('families', f'expected 9 boss families, got {len(families)}')
    fam_ids = [f.get('family_id') for f in families]
    for req in REQUIRED_FAMILIES:
        if req not in fam_ids:
            fail('families', f'missing required family {req!r}')
    for fid in fam_ids:
        if fid not in REQUIRED_FAMILIES:
            fail('families', f'unexpected family {fid!r}')

    # 3. global invariants
    gi = data.get('global_invariants') or {}
    if gi.get('marchio_owner_hero_id') != 'greek_borea':
        fail('global', 'marchio_owner_hero_id must be greek_borea')
    if gi.get('marchio_team_wide_amp_allowed') is not False:
        fail('global', 'marchio_team_wide_amp_allowed must be false')
    if gi.get('domain_one_active_per_side') is not True:
        fail('global', 'domain_one_active_per_side must be true')
    if gi.get('domain_no_same_turn_refresh') is not True:
        fail('global', 'domain_no_same_turn_refresh must be true')
    if gi.get('dw_phase_policy_design_only') is not True:
        fail('global', 'dw_phase_policy_design_only must be true')
    if gi.get('dw_live_numeric_modifier_applied') is not False:
        fail('global', 'dw_live_numeric_modifier_applied must be false')

    # 4. per-family checks
    for fam in families:
        fid = fam.get('family_id', '<unknown>')
        if fam.get('design_only') is not True:
            fail(fid, 'family.design_only must be true')
        if fam.get('runtime_attached') is not False:
            fail(fid, 'family.runtime_attached must be false')
        if fam.get('battle_runtime_attached') is not False:
            fail(fid, 'family.battle_runtime_attached must be false')

        # phase_model
        pm = fam.get('phase_model') or {}
        pc = pm.get('phase_count')
        if not isinstance(pc, int) or pc < 1 or pc > 4:
            fail(fid, f'phase_count must be 1..4 (got {pc!r})')
        thresholds = pm.get('hp_thresholds_pct')
        if not isinstance(thresholds, list):
            fail(fid, 'hp_thresholds_pct must be a list')
        else:
            # count must equal phase_count - 1
            if isinstance(pc, int) and len(thresholds) != max(0, pc - 1):
                fail(fid, f'hp_thresholds_pct count ({len(thresholds)}) must equal phase_count-1 ({max(0,pc-1)})')
            # strictly descending and within (0,100)
            for t in thresholds:
                if not (isinstance(t, (int, float)) and 0 < t < 100):
                    fail(fid, f'hp threshold {t!r} out of (0,100)')
            for i in range(1, len(thresholds)):
                if not (thresholds[i] < thresholds[i - 1]):
                    fail(fid, f'hp_thresholds_pct must be strictly descending: {thresholds}')
        labels = pm.get('phase_labels')
        if not isinstance(labels, list) or (isinstance(pc, int) and len(labels) != pc):
            fail(fid, f'phase_labels count must equal phase_count ({pc})')
        if pm.get('design_only') is not True:
            fail(fid, 'phase_model.design_only must be true')
        if pm.get('runtime_attached') is not False:
            fail(fid, 'phase_model.runtime_attached must be false')

        # enrage_policy
        ep = fam.get('enrage_policy') or {}
        if 'enabled' not in ep:
            fail(fid, 'enrage_policy.enabled missing')
        if not set(ep.get('trigger_types') or []).issubset(ALLOWED_TRIGGER_TYPES):
            fail(fid, f"enrage_policy.trigger_types invalid: {ep.get('trigger_types')}")
        dmg = ep.get('damage_multiplier_cap')
        spd = ep.get('speed_multiplier_cap')
        sct = ep.get('status_chance_multiplier_cap')
        max_dmg = DMG_CAP_BY_FAMILY[fid] if fid in DMG_CAP_BY_FAMILY else 1.50
        try:
            if not (0.95 <= float(dmg) <= max_dmg + 1e-9):
                fail(fid, f'damage_multiplier_cap {dmg} out of [0.95, {max_dmg}]')
            if fid == 'world_boss':
                if not (0.95 <= float(spd) <= 1.30 + 1e-9):
                    fail(fid, f'speed_multiplier_cap {spd} out of [0.95, 1.30]')
            else:
                if not (0.95 <= float(spd) <= 1.25 + 1e-9):
                    fail(fid, f'speed_multiplier_cap {spd} out of [0.95, 1.25]')
            if fid == 'pvp_dummy':
                if not (0.95 <= float(sct) <= 1.00 + 1e-9):
                    fail(fid, f'pvp_dummy status_chance_multiplier_cap {sct} must be <= 1.00')
            else:
                if not (0.95 <= float(sct) <= 1.15 + 1e-9):
                    fail(fid, f'status_chance_multiplier_cap {sct} out of [0.95, 1.15]')
        except (TypeError, ValueError):
            fail(fid, 'enrage_policy multiplier cap not numeric')
        # Training dummy: enrage disabled or capped <= 1.05
        if fid == 'training_dummy':
            if ep.get('enabled') is not False and float(dmg or 0) > 1.05 + 1e-9:
                fail(fid, 'training_dummy enrage not disabled and damage_multiplier_cap > 1.05')
        if fid == 'pvp_dummy':
            if ep.get('enabled') is not False:
                # if enabled, must be pvp_test_only and cap <= 1.05
                if not ep.get('pvp_test_only', False) or float(dmg or 0) > 1.05 + 1e-9:
                    fail(fid, 'pvp_dummy enrage must be disabled or pvp_test_only with cap<=1.05')
        if ep.get('design_only') is not True:
            fail(fid, 'enrage_policy.design_only must be true')
        if ep.get('runtime_attached') is not False:
            fail(fid, 'enrage_policy.runtime_attached must be false')

        # anti_loop_policy
        al = fam.get('anti_loop_policy') or {}
        for req in ('revive_per_unit_cap', 'revive_per_team_cap', 'shield_refresh_limit',
                    'healing_effectiveness_floor', 'healing_effectiveness_cap',
                    'hard_control_chain_limit', 'dot_stack_limit'):
            if req not in al:
                fail(fid, f'anti_loop_policy.{req} missing')
        try:
            rpu = int(al.get('revive_per_unit_cap', -1))
            rpt = int(al.get('revive_per_team_cap', -1))
            if fid not in ('training_dummy',):
                if rpu < 0 or rpu > 3:
                    fail(fid, f'revive_per_unit_cap {rpu} out of [0,3]')
                if rpt < 0 or rpt > 5:
                    fail(fid, f'revive_per_team_cap {rpt} out of [0,5]')
            hef = float(al.get('healing_effectiveness_floor', -1))
            hec = float(al.get('healing_effectiveness_cap', -1))
            if not (0.30 <= hef <= 1.00 + 1e-9):
                fail(fid, f'healing_effectiveness_floor {hef} out of [0.30, 1.00]')
            if not (0.50 <= hec <= 1.00 + 1e-9):
                fail(fid, f'healing_effectiveness_cap {hec} out of [0.50, 1.00]')
            if hef > hec + 1e-9:
                fail(fid, f'healing_effectiveness_floor ({hef}) > cap ({hec})')
            hcl = int(al.get('hard_control_chain_limit', -1))
            if fid == 'pvp_dummy':
                if hcl > 2:
                    fail(fid, f'pvp_dummy hard_control_chain_limit {hcl} > 2')
            elif fid != 'training_dummy':
                if hcl < 1 or hcl > 4:
                    fail(fid, f'hard_control_chain_limit {hcl} out of [1,4]')
        except (TypeError, ValueError):
            fail(fid, 'anti_loop numeric parse failure')
        if al.get('design_only') is not True:
            fail(fid, 'anti_loop_policy.design_only must be true')
        if al.get('runtime_attached') is not False:
            fail(fid, 'anti_loop_policy.runtime_attached must be false')

        # marchio_boreale_phase_policy
        mp = fam.get('marchio_boreale_phase_policy') or {}
        if mp.get('owner_hero_id') != 'greek_borea':
            fail(fid, 'marchio_boreale_phase_policy.owner_hero_id must be greek_borea')
        if mp.get('team_wide_amp_allowed') is not False:
            fail(fid, 'marchio_boreale_phase_policy.team_wide_amp_allowed must be false')
        if mp.get('no_activation') is not True:
            fail(fid, 'marchio_boreale_phase_policy.no_activation must be true')
        if mp.get('design_only') is not True:
            fail(fid, 'marchio_boreale_phase_policy.design_only must be true')
        if mp.get('runtime_attached') is not False:
            fail(fid, 'marchio_boreale_phase_policy.runtime_attached must be false')
        msbp = mp.get('max_stacks_by_phase')
        if not isinstance(msbp, list) or (isinstance(pc, int) and len(msbp) != pc):
            fail(fid, f'marchio max_stacks_by_phase length must equal phase_count ({pc})')
        else:
            for v in msbp:
                if not isinstance(v, int) or v < 0 or v > 4:
                    fail(fid, f'marchio max_stacks_by_phase entry {v} out of [0,4]')
        if mp.get('phase_transition_behavior') not in ALLOWED_TRANSITION_BEHAVIORS:
            fail(fid, f"marchio phase_transition_behavior invalid: {mp.get('phase_transition_behavior')!r}")

        # domain_phase_policy
        dp = fam.get('domain_phase_policy') or {}
        if dp.get('one_domain_active_per_side') is not True:
            fail(fid, 'domain_phase_policy.one_domain_active_per_side must be true')
        if dp.get('strongest_wins') is not True:
            fail(fid, 'domain_phase_policy.strongest_wins must be true')
        if dp.get('no_same_turn_refresh') is not True:
            fail(fid, 'domain_phase_policy.no_same_turn_refresh must be true')
        if dp.get('design_only') is not True:
            fail(fid, 'domain_phase_policy.design_only must be true')
        if dp.get('runtime_attached') is not False:
            fail(fid, 'domain_phase_policy.runtime_attached must be false')
        try:
            mdt = int(dp.get('max_duration_turns', -1))
            if not (1 <= mdt <= 5):
                fail(fid, f'domain max_duration_turns {mdt} out of [1,5]')
        except (TypeError, ValueError):
            fail(fid, 'domain max_duration_turns not int')

        # divine_weapon_phase_policy
        dwp = fam.get('divine_weapon_phase_policy') or {}
        if dwp.get('design_only') is not True:
            fail(fid, 'divine_weapon_phase_policy.design_only must be true')
        if dwp.get('live_numeric_modifier_applied') is not False:
            fail(fid, 'divine_weapon_phase_policy.live_numeric_modifier_applied must be false')
        if dwp.get('per_owner_only') is not True:
            fail(fid, 'divine_weapon_phase_policy.per_owner_only must be true')
        if dwp.get('runtime_attached') is not False:
            fail(fid, 'divine_weapon_phase_policy.runtime_attached must be false')

    # 5. no runtime/db hints anywhere
    check_no_true_runtime_flags(data, '$')
    check_no_db_hints(data, '$')

    # 6. source tables still present & intact (sanity)
    for src, label in ((RM134, 'RM1.34 table'), (RM134B, 'RM1.34-B matrix')):
        if not src.exists():
            fail('source', f'{label} missing: {src}')
        else:
            try:
                j = json.loads(src.read_text(encoding='utf-8'))
                if (j.get('metadata') or {}).get('design_only') is not True:
                    fail('source', f'{label} metadata.design_only must remain true')
            except Exception as e:
                fail('source', f'{label} parse error: {e}')

    if not BASELINE_V4.exists():
        fail('baseline', f'baseline v4 missing: {BASELINE_V4}')
    else:
        info(f'baseline v4 anchor present: {BASELINE_V4.name}')

    return emit()


def emit() -> int:
    print('=' * 72)
    print('RM1.34-C Boss Enrage / Phase Policy Table Validator')
    print('=' * 72)
    for i in infos: print(f'INFO: {i}')
    for w in warnings: print(f'WARN: {w}')
    if failures:
        print(f'\nFAILURES ({len(failures)}):')
        for f in failures: print(f'  - {f}')
        print('\nRESULT: FAIL')
        return 1
    print('\nRESULT: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
