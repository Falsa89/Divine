#!/usr/bin/env python3
"""
RM1.34-B — Boss Family × Element/Faction Resistance Matrix Validator (READ-ONLY)
────────────────────────────────────────────────────────────────────────────────
Validates `boss_family_element_faction_matrix_v1.json`.

This is a STRICT design-only validator. No DB writes, no runtime checks beyond
contract assertions. Exit 0 = PASS, 1 = FAIL.

Acceptance contract derived from RM1.34-B prompt:
- File exists and is valid JSON.
- metadata.task_origin = 'RM1.34-B' (top-level task_origin).
- design_only = true, runtime_attached = false, battle_runtime_attached = false,
  used_by_battle_engine = false, no_borea_activation = true.
- source includes `boss_family_resistance_table_v1`.
- Exactly 9 boss families matching the RM1.34 set.
- Required elements and faction groups present per family.
- Multipliers within safe ranges.
- training_dummy near-neutral (0.95..1.05) for damage/status/dot multipliers.
- pvp_dummy PvP-safe (no boss-hard resistances).
- combination_policy present per family with sane bounds:
  min_total_damage_taken_multiplier >= 0.50
  max_total_damage_taken_multiplier <= 1.50
- Marchio special case: owner = 'greek_borea', team_wide_amp_allowed = false.
- Divine Weapon synergy special case: design_only=true,
  live_numeric_modifier_applied=false.
- Domain special case: design_only=true.
- No runtime-* flags set true at any level.
- No DB write hints.
- boss_family_resistance_table_v1.json NOT modified content-wise from its own
  declared shape (sanity: file still present, design_only=true). We do NOT diff
  the table here; we only assert it is referenced as source and unchanged.
- baseline v4 file still exists (we do not re-hash here; baseline diff suite
  handles that), but matrix should declare it as anchor.
- Borea remains catalog-only via existing tests; we assert greek_borea has no
  visibility activation here.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
MATRIX = ROOT / 'data/design/boss_systems/boss_family_element_faction_matrix_v1.json'
TABLE = ROOT / 'data/design/boss_systems/boss_family_resistance_table_v1.json'
BASELINE_V4 = ROOT / 'data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132b_v4.json'
DELTA_PLAN = ROOT / 'data/design/hero_skill_kits/hero_skill_kits_balance_cap_delta_plan_v1.json'

REQUIRED_FAMILIES = (
    'story_boss', 'normal_boss', 'elite_boss', 'raid_boss',
    'world_boss', 'event_boss', 'guild_boss',
    'training_dummy', 'pvp_dummy',
)
REQUIRED_ELEMENTS = ('fire', 'water', 'earth', 'wind', 'lightning', 'light', 'darkness')
# RM1.34-B-PATCH-A allowed canonical element rename: darkness -> dark.
# Either spelling is accepted when matrix metadata declares the patch.
PATCH_A_RENAMED_ELEMENTS = {'darkness': 'dark'}
REQUIRED_FACTIONS = (
    'greek', 'norse', 'egyptian', 'japanese_yokai', 'celtic',
    'angelic', 'demonic', 'cursed', 'creature_beast',
    'primordial', 'arcane', 'tides', 'mesopotamian',
)
# RM1.34-B-PATCH-B allowed deferral set; these become optional when
# matrix metadata declares tides_status == 'deferred_not_live'.
PATCH_B_DEFERRED_FACTIONS = {'tides'}

# Per-prompt safe ranges
DTM_RANGE = (0.70, 1.30)
SCM_RANGE = (0.50, 1.20)
DOT_RANGE = (0.40, 1.10)

NEUTRAL_DUMMY_LO = 0.95
NEUTRAL_DUMMY_HI = 1.05

FORBIDDEN_RUNTIME_KEYS_TRUE = (
    'runtime_attached', 'battle_runtime_attached',
    'used_by_battle_engine', 'applied_to_combat',
    'patch_applied_to_catalogs', 'db_write',
)
FORBIDDEN_DB_WRITE_HINTS = ('db_write_active', 'mongo_write', 'sql_insert', 'persistence_active')

failures: list[str] = []
warnings: list[str] = []
infos: list[str] = []


def fail(sec: str, msg: str) -> None:
    failures.append(f'[{sec}] {msg}')


def warn(sec: str, msg: str) -> None:
    warnings.append(f'[{sec}] {msg}')


def info(msg: str) -> None:
    infos.append(msg)


def in_range(v, lo, hi) -> bool:
    try:
        return lo - 1e-9 <= float(v) <= hi + 1e-9
    except Exception:
        return False


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
    # 0. presence
    if not MATRIX.exists():
        fail('io', f'matrix file missing: {MATRIX}')
        return emit()
    try:
        data = json.loads(MATRIX.read_text(encoding='utf-8'))
    except Exception as e:
        fail('io', f'matrix JSON parse error: {e}')
        return emit()

    # 1. top-level identity
    if data.get('matrix_id') != 'boss_family_element_faction_matrix_v1':
        fail('meta', f"matrix_id mismatch (got {data.get('matrix_id')!r})")
    if data.get('task_origin') != 'RM1.34-B':
        fail('meta', f"task_origin != RM1.34-B (got {data.get('task_origin')!r})")
    sources = data.get('source_tables') or []
    if 'boss_family_resistance_table_v1' not in sources:
        fail('meta', 'source_tables missing boss_family_resistance_table_v1')
    else:
        info('source_tables references boss_family_resistance_table_v1')

    md = data.get('metadata') or {}
    # Post-patch tolerance: the matrix may have been mutated by
    # RM1.34-B-PATCH-A (darkness->dark) and RM1.34-B-PATCH-B (tides deferred).
    _patch_a = md.get('darkness_to_dark_applied') is True \
        and 'RM1.34-B-PATCH-A' in (md.get('axis_patches_applied') or [])
    _patch_b = md.get('tides_status') == 'deferred_not_live' \
        and 'RM1.34-B-PATCH-B' in (md.get('axis_patches_applied') or [])
    effective_required_elements = tuple(
        PATCH_A_RENAMED_ELEMENTS.get(e, e) if _patch_a else e
        for e in REQUIRED_ELEMENTS
    )
    effective_required_factions = tuple(
        f for f in REQUIRED_FACTIONS
        if not (_patch_b and f in PATCH_B_DEFERRED_FACTIONS)
    )

    if md.get('design_only') is not True:
        fail('meta', 'metadata.design_only must be true')
    if md.get('runtime_attached') is not False:
        fail('meta', 'metadata.runtime_attached must be false')
    if md.get('battle_runtime_attached') is not False:
        fail('meta', 'metadata.battle_runtime_attached must be false')
    if md.get('used_by_battle_engine') is not False:
        fail('meta', 'metadata.used_by_battle_engine must be false')
    if md.get('no_borea_activation') is not True:
        fail('meta', 'metadata.no_borea_activation must be true')
    if md.get('db_write') is not False:
        fail('meta', 'metadata.db_write must be false')
    if md.get('patch_applied_to_catalogs') is not False:
        fail('meta', 'metadata.patch_applied_to_catalogs must be false')
    if md.get('feature_flag_dependency') != 'SKILL_KIT_RUNTIME_ENABLED':
        fail('meta', 'feature_flag_dependency must be SKILL_KIT_RUNTIME_ENABLED')
    if md.get('feature_flag_currently_enabled') is not False:
        fail('meta', 'feature_flag_currently_enabled must be false')
    if md.get('baseline_anchor_at_creation') != 'hero_skill_kit_catalog_baseline_rm132b_v4':
        fail('meta', 'baseline_anchor_at_creation must be hero_skill_kit_catalog_baseline_rm132b_v4')

    # 2. elements / factions / families presence
    elems_top = data.get('elements_included') or []
    facs_top = data.get('faction_groups_included') or []
    for e in effective_required_elements:
        if e not in elems_top:
            fail('elements', f'missing element {e!r} in elements_included')
    for f in effective_required_factions:
        if f not in facs_top:
            fail('factions', f'missing faction {f!r} in faction_groups_included')

    families = data.get('boss_families') or []
    if len(families) != 9:
        fail('families', f'expected 9 boss families, got {len(families)}')
    fam_ids = [fam.get('family_id') for fam in families]
    for req in REQUIRED_FAMILIES:
        if req not in fam_ids:
            fail('families', f'missing family {req!r}')
    extras = [fid for fid in fam_ids if fid not in REQUIRED_FAMILIES]
    for ex in extras:
        fail('families', f'unexpected family {ex!r}')

    # 3. global invariants
    gi = data.get('global_invariants') or {}
    if gi.get('marchio_owner_hero_id') != 'greek_borea':
        fail('global', 'marchio_owner_hero_id must be greek_borea')
    if gi.get('marchio_team_wide_amp_allowed') is not False:
        fail('global', 'marchio_team_wide_amp_allowed must be false')
    if gi.get('dw_synergy_design_only') is not True:
        fail('global', 'dw_synergy_design_only must be true')
    if gi.get('dw_synergy_live_numeric_modifier_applied') is not False:
        fail('global', 'dw_synergy_live_numeric_modifier_applied must be false')
    if gi.get('domain_one_active_per_side') is not True:
        fail('global', 'domain_one_active_per_side must be true')

    # 4. per-family checks
    for fam in families:
        fid = fam.get('family_id', '<unknown>')
        if fam.get('runtime_attached') is not False:
            fail(fid, 'runtime_attached must be false')
        if fam.get('battle_runtime_attached') is not False:
            fail(fid, 'battle_runtime_attached must be false')
        if fam.get('design_only') is not True:
            fail(fid, 'design_only must be true')

        # element modifiers
        ems = fam.get('element_resistance_modifiers') or {}
        for el in effective_required_elements:
            if el not in ems:
                fail(fid, f'missing element_resistance_modifiers.{el}')
                continue
            row = ems[el] or {}
            dtm = row.get('damage_taken_multiplier')
            scm = row.get('status_chance_multiplier')
            dot = row.get('dot_tick_multiplier')
            if not in_range(dtm, *DTM_RANGE):
                fail(fid, f'element {el}: damage_taken_multiplier {dtm} out of {DTM_RANGE}')
            if not in_range(scm, *SCM_RANGE):
                fail(fid, f'element {el}: status_chance_multiplier {scm} out of {SCM_RANGE}')
            if not in_range(dot, *DOT_RANGE):
                fail(fid, f'element {el}: dot_tick_multiplier {dot} out of {DOT_RANGE}')
            # Training dummy neutrality
            if fid == 'training_dummy':
                for label, v in (('damage_taken_multiplier', dtm),
                                 ('status_chance_multiplier', scm),
                                 ('dot_tick_multiplier', dot)):
                    if not in_range(v, NEUTRAL_DUMMY_LO, NEUTRAL_DUMMY_HI):
                        fail(fid, f'training_dummy element {el}.{label} {v} not within neutral band {NEUTRAL_DUMMY_LO}..{NEUTRAL_DUMMY_HI}')
            # PvP dummy neutrality (PvP-safe)
            if fid == 'pvp_dummy':
                for label, v in (('damage_taken_multiplier', dtm),
                                 ('status_chance_multiplier', scm),
                                 ('dot_tick_multiplier', dot)):
                    if not in_range(v, NEUTRAL_DUMMY_LO, NEUTRAL_DUMMY_HI):
                        fail(fid, f'pvp_dummy element {el}.{label} {v} not within neutral band {NEUTRAL_DUMMY_LO}..{NEUTRAL_DUMMY_HI}')

        # faction modifiers
        fms = fam.get('faction_resistance_modifiers') or {}
        for fac in effective_required_factions:
            if fac not in fms:
                fail(fid, f'missing faction_resistance_modifiers.{fac}')
                continue
            row = fms[fac] or {}
            dtm = row.get('damage_taken_multiplier')
            scm = row.get('status_chance_multiplier')
            if not in_range(dtm, *DTM_RANGE):
                fail(fid, f'faction {fac}: damage_taken_multiplier {dtm} out of {DTM_RANGE}')
            if not in_range(scm, *SCM_RANGE):
                fail(fid, f'faction {fac}: status_chance_multiplier {scm} out of {SCM_RANGE}')
            tags = row.get('special_rule_tags')
            if tags is None or not isinstance(tags, list):
                fail(fid, f'faction {fac}: special_rule_tags must be list')
            if fid == 'training_dummy':
                if not in_range(dtm, NEUTRAL_DUMMY_LO, NEUTRAL_DUMMY_HI):
                    fail(fid, f'training_dummy faction {fac}.damage_taken_multiplier {dtm} not neutral')
                if not in_range(scm, NEUTRAL_DUMMY_LO, NEUTRAL_DUMMY_HI):
                    fail(fid, f'training_dummy faction {fac}.status_chance_multiplier {scm} not neutral')
            if fid == 'pvp_dummy':
                if not in_range(dtm, NEUTRAL_DUMMY_LO, NEUTRAL_DUMMY_HI):
                    fail(fid, f'pvp_dummy faction {fac}.damage_taken_multiplier {dtm} not PvP-safe neutral')
                if not in_range(scm, NEUTRAL_DUMMY_LO, NEUTRAL_DUMMY_HI):
                    fail(fid, f'pvp_dummy faction {fac}.status_chance_multiplier {scm} not PvP-safe neutral')

        # combination policy
        cp = fam.get('combination_policy') or {}
        if cp.get('element_and_faction_stack_mode') not in ('multiplicative', 'additive', 'capped_multiplicative'):
            fail(fid, f"combination_policy.element_and_faction_stack_mode invalid: {cp.get('element_and_faction_stack_mode')!r}")
        mn = cp.get('min_total_damage_taken_multiplier')
        mx = cp.get('max_total_damage_taken_multiplier')
        try:
            if float(mn) < 0.50:
                fail(fid, f'min_total_damage_taken_multiplier {mn} < 0.50')
            if float(mx) > 1.50:
                fail(fid, f'max_total_damage_taken_multiplier {mx} > 1.50')
            if float(mn) >= float(mx):
                fail(fid, f'min ({mn}) must be < max ({mx})')
        except Exception:
            fail(fid, 'combination_policy min/max not numeric')
        if fid == 'pvp_dummy' and cp.get('pvp_dummy_override') is not True:
            fail(fid, 'pvp_dummy must set combination_policy.pvp_dummy_override=true')
        if fid != 'pvp_dummy' and cp.get('pvp_dummy_override') is True:
            fail(fid, 'pvp_dummy_override true only valid for pvp_dummy family')
        if 'boss_family_priority' not in cp:
            fail(fid, 'combination_policy.boss_family_priority missing')

        # special cases
        sc = fam.get('special_cases') or {}
        # Marchio
        m = sc.get('marchio_boreale') or {}
        if m.get('owner_hero_id') != 'greek_borea':
            fail(fid, "marchio_boreale.owner_hero_id must be greek_borea")
        if m.get('team_wide_amp_allowed') is not False:
            fail(fid, 'marchio_boreale.team_wide_amp_allowed must be false')
        if m.get('design_only') is not True:
            fail(fid, 'marchio_boreale.design_only must be true')
        if m.get('runtime_ready') is not False:
            fail(fid, 'marchio_boreale.runtime_ready must be false')
        # DW synergy
        dw = sc.get('divine_weapon_synergy') or {}
        if dw.get('design_only') is not True:
            fail(fid, 'divine_weapon_synergy.design_only must be true')
        if dw.get('live_numeric_modifier_applied') is not False:
            fail(fid, 'divine_weapon_synergy.live_numeric_modifier_applied must be false')
        # Domain
        de = sc.get('domain_effect') or {}
        if de.get('design_only') is not True:
            fail(fid, 'domain_effect.design_only must be true')
        if de.get('runtime_ready') is not False:
            fail(fid, 'domain_effect.runtime_ready must be false')

    # 5. no true runtime keys anywhere
    check_no_true_runtime_flags(data, '$')
    check_no_db_hints(data, '$')

    # 6. baseline v4 still present (anchor sanity, not a diff)
    if not BASELINE_V4.exists():
        fail('baseline', f'baseline v4 missing: {BASELINE_V4}')
    else:
        info(f'baseline v4 anchor present: {BASELINE_V4.name}')

    # 7. boss family resistance table v1 still present
    if not TABLE.exists():
        fail('source', f'boss_family_resistance_table_v1.json missing: {TABLE}')
    else:
        try:
            tbl = json.loads(TABLE.read_text(encoding='utf-8'))
            md_tbl = tbl.get('metadata') or {}
            if md_tbl.get('design_only') is not True:
                fail('source', 'boss_family_resistance_table_v1 metadata.design_only must remain true')
            if tbl.get('task_origin') != 'RM1.34':
                fail('source', 'boss_family_resistance_table_v1 task_origin must remain RM1.34')
        except Exception as e:
            fail('source', f'boss_family_resistance_table_v1 parse error: {e}')

    return emit()


def emit() -> int:
    print('=' * 72)
    print('RM1.34-B Boss Family × Element/Faction Matrix Validator')
    print('=' * 72)
    if infos:
        for i in infos:
            print(f'INFO: {i}')
    if warnings:
        for w in warnings:
            print(f'WARN: {w}')
    if failures:
        print(f'\nFAILURES ({len(failures)}):')
        for f in failures:
            print(f'  - {f}')
        print('\nRESULT: FAIL')
        return 1
    print('\nRESULT: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
