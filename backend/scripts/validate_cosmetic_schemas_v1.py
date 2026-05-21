#!/usr/bin/env python3
"""COSMETIC-A: Validate schemas (read-only)."""
import json, re, sys
from datetime import datetime, timezone
from pathlib import Path
OUT = Path('/app/data/design/cosmetics/_validate_cosmetic_schemas_v1_result.json')
ROOT = Path('/app/data/design/cosmetics')
SCHEMAS = [
    ('skin_catalog_schema_v1.json', ['skin_id','hero_id','display_name','rarity','source_type','scope_type','is_limited','rerun_policy','unlock_condition_ids','bonus_profile','asset_status','design_only','runtime_attached','battle_runtime_attached']),
    ('title_catalog_schema_v1.json', ['title_id','display_name','rarity','source_type','scope_type','equip_limit_group','bonus_profile','unlock_condition_ids','seasonality','server_first_allowed','design_only','runtime_attached','battle_runtime_attached']),
    ('cosmetic_bonus_schema_v1.json', ['bonus_types','bonus_entry_schema','normalization_rules','resolver_contract']),
    ('cosmetic_unlock_condition_schema_v1.json', ['condition_types','required_fields','field_specs']),
    ('cosmetic_equipment_state_schema_v1.json', ['player_state_schema','invariants']),
    ('cosmetic_prestige_score_schema_v1.json', ['contribution_by_rarity','contribution_by_kind','caps','score_to_bonus_curve']),
]
BONUS_TYPES_REQUIRED = [
    'team_hp_flat','team_atk_flat','team_def_flat','team_hp_pct','team_atk_pct','team_def_pct',
    'hero_hp_pct','hero_atk_pct','hero_def_pct','role_bonus_pct','faction_bonus_pct','element_bonus_pct',
    'initial_rage_flat','speed_flat','boss_damage_pct','pve_damage_pct','pvp_damage_pct','guild_war_damage_pct',
    'damage_reduction_pct','healing_done_pct','shield_strength_pct',
    'gold_gain_pct','account_exp_gain_pct','affinity_gain_pct','gift_value_pct','material_drop_pct','prestige_score_flat',
]
COND_TYPES_REQUIRED = [
    'topup_amount_event','paid_crystal_purchase','pvp_rank_reached','tower_floor_reached','weekly_castle_clears',
    'zodiac_house_commander_hours','hero_affinity_level','titan_kill_count','guild_war_kill_streak','guild_war_kills_cumulative',
    'event_wins_count','battle_power_reached','hero_star_reached','server_first_achievement','seasonal_event_completion',
]


def main():
    errs=[]; checked=[]
    for fn, required in SCHEMAS:
        p=ROOT/fn
        checked.append(fn)
        if not p.exists(): errs.append(f'missing:{fn}'); continue
        try: d=json.loads(p.read_text())
        except Exception as e: errs.append(f'parse:{fn}:{e}'); continue
        if not d.get('design_only'): errs.append(f'{fn}:not_design_only')
        if d.get('runtime_attached'): errs.append(f'{fn}:runtime_attached')
        if d.get('battle_runtime_attached'): errs.append(f'{fn}:battle_attached')
        rf = d.get('required_fields') or list(d.keys())
        for k in required:
            if k not in rf and k not in d:
                errs.append(f'{fn}:missing_field:{k}')
        # title schema must have equip_limit_group=='active_title'
        if fn == 'title_catalog_schema_v1.json':
            spec = (d.get('field_specs') or {}).get('equip_limit_group') or {}
            if spec.get('const') != 'active_title':
                errs.append(f'{fn}:equip_limit_group_not_active_title')
            if d.get('max_active_title_per_player') != 1:
                errs.append(f'{fn}:max_active_title_not_1')
        # skin schema must forbid borea hero_ids
        if fn == 'skin_catalog_schema_v1.json':
            forbidden = d.get('forbidden_hero_ids') or []
            for b in ('borea','greek_borea','primordial_gaia'):
                if b not in forbidden:
                    errs.append(f'{fn}:borea_not_forbidden:{b}')
        # bonus schema must include all required bonus types
        if fn == 'cosmetic_bonus_schema_v1.json':
            present = set(d.get('bonus_types') or [])
            for bt in BONUS_TYPES_REQUIRED:
                if bt not in present:
                    errs.append(f'{fn}:missing_bonus_type:{bt}')
        # unlock condition schema must include all required condition types
        if fn == 'cosmetic_unlock_condition_schema_v1.json':
            present = set(d.get('condition_types') or [])
            for ct in COND_TYPES_REQUIRED:
                if ct not in present:
                    errs.append(f'{fn}:missing_condition_type:{ct}')

    out = {
        'task_origin':'COSMETIC-A-VALIDATE-SCHEMAS',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'files_checked': checked,
        'errors': errs,
        'verdict': 'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out,indent=2,default=str))
    print(f"verdict={out['verdict']} errors={len(errs)}")
    for e in errs[:20]: print(f'  - {e}')
    return 0 if not errs else 2


if __name__ == '__main__': sys.exit(main())
