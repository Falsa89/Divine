#!/usr/bin/env python3
"""
RM1.32-B — 6★ Balance Pass Foundation Builder
─────────────────────────────────────────────────────────────────────────
ONE-SHOT builder that performs the patch operation:

  1. Generates the 6★ balance contract JSON.
  2. Generates the 6★ balance foundation source JSON.
  3. Backs up the 6★ catalog (via existing backup helper).
  4. Patches the 6★ catalog in-place by adding `final_numbers` blocks
     to all 78 slots + balance metadata top-level. NOTHING else changes.

The catalog patch ONLY touches:
  - `final_numbers` field on each slot (currently null → object)
  - top-level: `balance_pass_id`, `last_balance_foundation_write`
  - Does NOT touch any other field, slot, status, tag, weapon id, etc.

Safety:
  - status="foundation_draft", runtime_ready=false on every block
  - top-level runtime_attached/battle_runtime_attached/balance_values_finalized
    stay false
  - Marchio Boreale draft values appear ONLY on greek_borea
  - design_only=true on synergy placeholders / unique mechanics
  - NO DB / runtime / gacha / roster / Borea visibility changes

Run:
  python3 /app/backend/scripts/rm132b_build_6star_balance_foundation.py
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/app')
HSK_6STAR = ROOT / 'data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json'
CONTRACT_OUT = ROOT / 'data/design/hero_skill_kits/hero_skill_kits_6star_balance_contract_v1.json'
SOURCE_OUT = ROOT / 'data/design/hero_skill_kits/hero_skill_kits_6star_balance_foundation_source_v1.json'

# ───────────────────────────── archetypes ────────────────────────────────
ARCHETYPE_OF = {
    'greek_athena':                'tank_support',
    'greek_artemis':               'ranged_dps',
    'greek_gaia':                  'tank_revive',
    'primordial_nyx':              'aoe_control_mage',
    'japanese_raijin':             'aoe_dps_mage',
    'japanese_susanoo':            'assassin_burst',
    'japanese_amaterasu':          'healer_buffer',
    'egyptian_sekhmet':            'melee_dps',
    'mesopotamian_tiamat':         'tank_aoe',
    'egyptian_isis':               'healer_revive',
    'celtic_morrigan':             'assassin_control',
    'cursed_pestilence_horseman':  'control_dot',
    'greek_borea':                 'control_mage_freeze',
}

# Conservative per-archetype/per-slot value template.
# Numbers chosen near the lower / mid band of the prompt's allowed ranges.
PROFILES = {
    # ───── TANK / GUARDIAN ──────────────────────────────────────────────
    'tank_support': {
        'basic': dict(scaling_stat='def',   tier='medium',
                      dmg=100, status_chance=30, status_dur=1,
                      cd=0, tgt=1),
        'passive_base': dict(scaling_stat='def', tier='medium',
                             stat_mod=14, internal_cd=None),
        'skill_1': dict(scaling_stat='def', tier='medium',
                        dmg=170, shield=200, heal=None,
                        status_chance=70, status_dur=2, cd=3, tgt=3),
        'passive_advanced': dict(scaling_stat='def', tier='high',
                                 stat_mod=20, internal_cd=3),
        'skill_2': dict(scaling_stat='def', tier='high',
                        dmg=240, shield=300, heal=None,
                        status_chance=85, status_dur=2, cd=5, tgt=5),
        'ultimate': dict(scaling_stat='def', tier='legendary_foundation',
                         dmg=360, shield=460, heal=None,
                         status_chance=95, status_dur=3, cd=7, tgt=5),
    },
    'tank_revive': {
        'basic': dict(scaling_stat='max_hp', tier='medium',
                      dmg=100, status_chance=30, status_dur=1, cd=0, tgt=1),
        'passive_base': dict(scaling_stat='max_hp', tier='medium',
                             stat_mod=15, internal_cd=None),
        'skill_1': dict(scaling_stat='max_hp', tier='medium',
                        dmg=170, shield=210, heal=190,
                        status_chance=65, status_dur=2, cd=3, tgt=3),
        'passive_advanced': dict(scaling_stat='max_hp', tier='high',
                                 stat_mod=22, internal_cd=4),
        'skill_2': dict(scaling_stat='max_hp', tier='high',
                        dmg=240, shield=300, heal=280,
                        status_chance=80, status_dur=2, cd=5, tgt=5),
        'ultimate': dict(scaling_stat='max_hp', tier='legendary_foundation',
                         dmg=340, shield=480, heal=460,
                         status_chance=95, status_dur=3, cd=7, tgt=5),
    },
    'tank_aoe': {
        'basic': dict(scaling_stat='max_hp', tier='medium',
                      dmg=110, status_chance=35, status_dur=1, cd=0, tgt=1),
        'passive_base': dict(scaling_stat='max_hp', tier='medium',
                             stat_mod=15, internal_cd=None),
        'skill_1': dict(scaling_stat='max_hp', tier='medium',
                        dmg=180, shield=200, heal=None,
                        status_chance=70, status_dur=2, cd=3, tgt=5),
        'passive_advanced': dict(scaling_stat='max_hp', tier='high',
                                 stat_mod=20, internal_cd=3),
        'skill_2': dict(scaling_stat='max_hp', tier='high',
                        dmg=260, shield=280, heal=None,
                        status_chance=85, status_dur=2, cd=5, tgt=5),
        'ultimate': dict(scaling_stat='max_hp', tier='legendary_foundation',
                         dmg=400, shield=420, heal=None,
                         status_chance=95, status_dur=3, cd=7, tgt=5),
    },
    # ───── DPS ──────────────────────────────────────────────────────────
    'ranged_dps': {
        'basic': dict(scaling_stat='atk', tier='medium',
                      dmg=120, status_chance=30, status_dur=1, cd=0, tgt=1),
        'passive_base': dict(scaling_stat='atk', tier='medium',
                             stat_mod=16, internal_cd=None),
        'skill_1': dict(scaling_stat='atk', tier='high',
                        dmg=260, shield=None, heal=None,
                        status_chance=75, status_dur=2, cd=3, tgt=1),
        'passive_advanced': dict(scaling_stat='atk', tier='high',
                                 stat_mod=22, internal_cd=3),
        'skill_2': dict(scaling_stat='atk', tier='high',
                        dmg=420, shield=None, heal=None,
                        status_chance=85, status_dur=2, cd=5, tgt=1),
        'ultimate': dict(scaling_stat='atk', tier='legendary_foundation',
                         dmg=680, shield=None, heal=None,
                         status_chance=95, status_dur=2, cd=7, tgt=1),
    },
    'melee_dps': {
        'basic': dict(scaling_stat='atk', tier='medium',
                      dmg=120, status_chance=35, status_dur=1, cd=0, tgt=1),
        'passive_base': dict(scaling_stat='atk', tier='medium',
                             stat_mod=18, internal_cd=None),
        'skill_1': dict(scaling_stat='atk', tier='high',
                        dmg=280, shield=None, heal=None,
                        status_chance=80, status_dur=2, cd=3, tgt=1),
        'passive_advanced': dict(scaling_stat='atk', tier='high',
                                 stat_mod=24, internal_cd=3),
        'skill_2': dict(scaling_stat='atk', tier='high',
                        dmg=440, shield=None, heal=None,
                        status_chance=90, status_dur=2, cd=5, tgt=3),
        'ultimate': dict(scaling_stat='atk', tier='legendary_foundation',
                         dmg=700, shield=None, heal=None,
                         status_chance=95, status_dur=2, cd=7, tgt=1),
    },
    'assassin_burst': {
        'basic': dict(scaling_stat='atk', tier='medium',
                      dmg=125, status_chance=30, status_dur=1, cd=0, tgt=1),
        'passive_base': dict(scaling_stat='atk', tier='medium',
                             stat_mod=18, internal_cd=None),
        'skill_1': dict(scaling_stat='atk', tier='high',
                        dmg=320, shield=None, heal=None,
                        status_chance=80, status_dur=2, cd=3, tgt=1),
        'passive_advanced': dict(scaling_stat='atk', tier='high',
                                 stat_mod=26, internal_cd=3),
        'skill_2': dict(scaling_stat='atk', tier='high',
                        dmg=500, shield=None, heal=None,
                        status_chance=90, status_dur=2, cd=5, tgt=1),
        'ultimate': dict(scaling_stat='atk', tier='legendary_foundation',
                         dmg=720, shield=None, heal=None,
                         status_chance=95, status_dur=2, cd=6, tgt=1),
    },
    'assassin_control': {
        'basic': dict(scaling_stat='atk', tier='medium',
                      dmg=120, status_chance=40, status_dur=1, cd=0, tgt=1),
        'passive_base': dict(scaling_stat='atk', tier='medium',
                             stat_mod=16, internal_cd=None),
        'skill_1': dict(scaling_stat='atk', tier='high',
                        dmg=300, shield=None, heal=None,
                        status_chance=85, status_dur=2, cd=3, tgt=1),
        'passive_advanced': dict(scaling_stat='atk', tier='high',
                                 stat_mod=24, internal_cd=3),
        'skill_2': dict(scaling_stat='atk', tier='high',
                        dmg=480, shield=None, heal=None,
                        status_chance=90, status_dur=2, cd=5, tgt=3),
        'ultimate': dict(scaling_stat='atk', tier='legendary_foundation',
                         dmg=700, shield=None, heal=None,
                         status_chance=95, status_dur=3, cd=7, tgt=1),
    },
    'aoe_dps_mage': {
        'basic': dict(scaling_stat='atk', tier='medium',
                      dmg=115, status_chance=30, status_dur=1, cd=0, tgt=1),
        'passive_base': dict(scaling_stat='atk', tier='medium',
                             stat_mod=15, internal_cd=None),
        'skill_1': dict(scaling_stat='atk', tier='high',
                        dmg=180, shield=None, heal=None,
                        status_chance=70, status_dur=2, cd=3, tgt=5),
        'passive_advanced': dict(scaling_stat='atk', tier='high',
                                 stat_mod=22, internal_cd=3),
        'skill_2': dict(scaling_stat='atk', tier='high',
                        dmg=280, shield=None, heal=None,
                        status_chance=85, status_dur=2, cd=5, tgt=5),
        'ultimate': dict(scaling_stat='atk', tier='legendary_foundation',
                         dmg=440, shield=None, heal=None,
                         status_chance=95, status_dur=2, cd=7, tgt=5),
    },
    'aoe_control_mage': {
        'basic': dict(scaling_stat='atk', tier='medium',
                      dmg=110, status_chance=35, status_dur=1, cd=0, tgt=1),
        'passive_base': dict(scaling_stat='atk', tier='medium',
                             stat_mod=14, internal_cd=None),
        'skill_1': dict(scaling_stat='atk', tier='high',
                        dmg=170, shield=None, heal=None,
                        status_chance=80, status_dur=2, cd=3, tgt=5),
        'passive_advanced': dict(scaling_stat='atk', tier='high',
                                 stat_mod=22, internal_cd=3),
        'skill_2': dict(scaling_stat='atk', tier='high',
                        dmg=260, shield=None, heal=None,
                        status_chance=90, status_dur=2, cd=5, tgt=5),
        'ultimate': dict(scaling_stat='atk', tier='legendary_foundation',
                         dmg=380, shield=None, heal=None,
                         status_chance=95, status_dur=3, cd=7, tgt=5),
    },
    'control_dot': {
        'basic': dict(scaling_stat='atk', tier='medium',
                      dmg=110, status_chance=35, status_dur=2, cd=0, tgt=1),
        'passive_base': dict(scaling_stat='atk', tier='medium',
                             stat_mod=14, internal_cd=None),
        'skill_1': dict(scaling_stat='atk', tier='high',
                        dmg=180, shield=None, heal=None,
                        status_chance=80, status_dur=2, cd=3, tgt=5),
        'passive_advanced': dict(scaling_stat='atk', tier='high',
                                 stat_mod=20, internal_cd=3),
        'skill_2': dict(scaling_stat='atk', tier='high',
                        dmg=260, shield=None, heal=None,
                        status_chance=90, status_dur=2, cd=5, tgt=5),
        'ultimate': dict(scaling_stat='atk', tier='legendary_foundation',
                         dmg=380, shield=None, heal=None,
                         status_chance=95, status_dur=3, cd=7, tgt=5),
    },
    'control_mage_freeze': {
        'basic': dict(scaling_stat='atk', tier='medium',
                      dmg=110, status_chance=35, status_dur=1, cd=0, tgt=1),
        'passive_base': dict(scaling_stat='atk', tier='medium',
                             stat_mod=15, internal_cd=None),
        'skill_1': dict(scaling_stat='atk', tier='high',
                        dmg=180, shield=None, heal=None,
                        status_chance=80, status_dur=2, cd=3, tgt=3),
        'passive_advanced': dict(scaling_stat='atk', tier='high',
                                 stat_mod=22, internal_cd=3),
        'skill_2': dict(scaling_stat='atk', tier='high',
                        dmg=280, shield=None, heal=None,
                        status_chance=90, status_dur=2, cd=5, tgt=5),
        'ultimate': dict(scaling_stat='atk', tier='legendary_foundation',
                         dmg=400, shield=None, heal=None,
                         status_chance=95, status_dur=3, cd=7, tgt=5),
    },
    # ───── HEALER / SUPPORT ──────────────────────────────────────────────
    'healer_buffer': {
        'basic': dict(scaling_stat='atk', tier='medium',
                      dmg=95, status_chance=30, status_dur=1, cd=0, tgt=1),
        'passive_base': dict(scaling_stat='atk', tier='medium',
                             stat_mod=14, internal_cd=None),
        'skill_1': dict(scaling_stat='atk', tier='high',
                        dmg=None, shield=190, heal=210,
                        status_chance=70, status_dur=2, cd=3, tgt=5),
        'passive_advanced': dict(scaling_stat='atk', tier='high',
                                 stat_mod=22, internal_cd=3),
        'skill_2': dict(scaling_stat='atk', tier='high',
                        dmg=None, shield=280, heal=300,
                        status_chance=80, status_dur=2, cd=5, tgt=5),
        'ultimate': dict(scaling_stat='atk', tier='legendary_foundation',
                         dmg=None, shield=440, heal=500,
                         status_chance=95, status_dur=3, cd=7, tgt=5),
    },
    'healer_revive': {
        'basic': dict(scaling_stat='atk', tier='medium',
                      dmg=90, status_chance=30, status_dur=1, cd=0, tgt=1),
        'passive_base': dict(scaling_stat='atk', tier='medium',
                             stat_mod=14, internal_cd=None),
        'skill_1': dict(scaling_stat='atk', tier='high',
                        dmg=None, shield=190, heal=220,
                        status_chance=70, status_dur=2, cd=3, tgt=5),
        'passive_advanced': dict(scaling_stat='atk', tier='high',
                                 stat_mod=22, internal_cd=4),
        'skill_2': dict(scaling_stat='atk', tier='high',
                        dmg=None, shield=300, heal=320,
                        status_chance=80, status_dur=2, cd=5, tgt=5),
        'ultimate': dict(scaling_stat='atk', tier='legendary_foundation',
                         dmg=None, shield=460, heal=520,
                         status_chance=95, status_dur=3, cd=7, tgt=5),
    },
}

# Borea unique design-only Marchio Boreale draft values (catalog-only).
MARCHIO_BOREALE_DRAFT = {
    "design_only": True,
    "personal_status_id": "marchio_boreale",
    "owner_hero_id": "greek_borea",
    "max_stacks_pvp": 3,
    "max_stacks_pve": 5,
    "damage_bonus_per_stack_pct": 7,
    "freeze_chance_bonus_per_stack_pct": 4,
    "decay_rule": "design_only: 1 stack decays at end of marked unit turn unless re-applied; resets fully on cleanse",
    "cleanse_rule": "design_only: standard cleanse removes all stacks at once; cannot be partially cleansed",
    "boss_resistance_notes": "design_only: bosses cap effective stacks at max_stacks_pve - 1; PvE-only design space",
    "pvp_caution_notes": "design_only: in PvP the max stacks is conservative (3) to prevent runaway snowball; foundation_draft only",
    "runtime_ready": False,
}

# Forbidden runtime indicators for slot blocks
FORBIDDEN_FIELDS = {
    "final_runtime_attached", "battle_runtime_id", "live_hooks",
    "db_resolver", "runtime_target", "vfx_runtime",
}

# ───────────────────────────── helpers ───────────────────────────────────
NOW_UTC = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build_final_numbers(hero_id: str, slot_name: str, archetype: str) -> dict:
    prof = PROFILES[archetype][slot_name]
    is_passive = slot_name.startswith('passive')
    is_ultimate = (slot_name == 'ultimate')

    if is_passive:
        fn = {
            "status": "foundation_draft",
            "runtime_ready": False,
            "trigger": ("on_low_hp_self" if slot_name == 'passive_advanced'
                        else "on_battle_start"),
            "stat_modifier_pct": prof['stat_mod'],
            "status_chance_pct": None,
            "status_duration_turns": None,
            "internal_cooldown_turns": prof['internal_cd'],
            "scaling_stat": prof['scaling_stat'],
            "effect_strength_tier": prof['tier'],
            "draft_balance_notes": (
                f"{archetype} {slot_name}: conservative foundation_draft passive; "
                "design-only; not runtime."
            ),
            "review_required": False,
            "runtime_notes": "foundation draft; not runtime",
            "notes": "foundation draft; not runtime",
        }
    else:
        fn = {
            "status": "foundation_draft",
            "runtime_ready": False,
            "scaling_stat": prof['scaling_stat'],
            "effect_strength_tier": prof['tier'],
            "cooldown_turns": prof['cd'],
            "target_count": prof['tgt'],
            "status_chance_pct": prof['status_chance'],
            "status_duration_turns": prof['status_dur'],
            "damage_multiplier_pct": prof.get('dmg'),
            "healing_multiplier_pct": prof.get('heal'),
            "shield_multiplier_pct": prof.get('shield'),
            "stat_modifier_pct": None,
            "runtime_notes": "foundation draft; not runtime",
            "review_required": False,
            "draft_balance_notes": (
                f"{archetype} {slot_name}: conservative 6★ foundation_draft; "
                "design-only; not runtime."
            ),
            "notes": "foundation draft; not runtime",
        }
        if is_ultimate:
            fn["is_true_ultimate"] = True

    # Add Divine Weapon synergy placeholder (design-only)
    fn["divine_weapon_synergy_placeholder"] = {
        "design_only": True,
        "runtime_ready": False,
        "linked_weapon_id_from_entry": True,
        "synergy_intent": (
            f"design-only descriptor: {hero_id}'s 6★ {slot_name} resonates with "
            f"its divine_weapon_id at narrative/VFX taxonomy level only; "
            "no numeric runtime modifier applied at this foundation pass."
        ),
        "numeric_modifier_pct": None,
    }

    # Marchio Boreale draft values: ONLY on greek_borea slots (where relevant).
    if hero_id == 'greek_borea' and not is_passive:
        fn["marchio_boreale_stack_values"] = dict(MARCHIO_BOREALE_DRAFT)
        fn["unique_mechanic_placeholder"] = {
            "design_only": True,
            "runtime_ready": False,
            "mechanic_id": "marchio_boreale",
            "exclusive_to_hero": "greek_borea",
            "notes": (
                "Marchio Boreale is a personal/unique status owned solely by greek_borea. "
                "Stack values listed here are design_only foundation_draft; runtime hookup deferred."
            ),
        }

    return fn


def build_source_entry(hero_id: str) -> dict:
    arch = ARCHETYPE_OF[hero_id]
    slots = {}
    for sn in ('basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2', 'ultimate'):
        slots[sn] = build_final_numbers(hero_id, sn, arch)
    return {
        "hero_id": hero_id,
        "archetype": arch,
        "rationale": f"6★ conservative foundation_draft values for archetype '{arch}'.",
        "slots": slots,
    }


# ───────────────────────────── contract ──────────────────────────────────
def build_contract() -> dict:
    common_slot_fields = [
        "status", "runtime_ready",
        "scaling_stat", "effect_strength_tier",
        "cooldown_turns", "target_count",
        "status_chance_pct", "status_duration_turns",
        "damage_multiplier_pct", "healing_multiplier_pct", "shield_multiplier_pct",
        "stat_modifier_pct",
        "runtime_notes", "review_required",
        "draft_balance_notes", "notes",
        "divine_weapon_synergy_placeholder",
    ]
    passive_fields = [
        "status", "runtime_ready",
        "trigger", "stat_modifier_pct",
        "status_chance_pct", "status_duration_turns",
        "internal_cooldown_turns",
        "scaling_stat", "effect_strength_tier",
        "runtime_notes", "review_required",
        "draft_balance_notes", "notes",
        "divine_weapon_synergy_placeholder",
    ]
    ultimate_fields = common_slot_fields + ["is_true_ultimate"]
    borea_only_fields = [
        "marchio_boreale_stack_values",
        "unique_mechanic_placeholder",
    ]
    return {
        "contract_id": "hero_skill_kits_6star_balance_contract_v1",
        "task_origin": "RM1.32-B",
        "generated_at_utc": NOW_UTC,
        "scope": "6★ catalog (13 heroes × 6 slots = 78 slots). Foundation balance pass — design data only.",
        "allowed_fields_per_slot": {
            "basic":           common_slot_fields,
            "passive_base":    passive_fields,
            "skill_1":         common_slot_fields,
            "passive_advanced": passive_fields,
            "skill_2":         common_slot_fields,
            "ultimate":        ultimate_fields,
        },
        "borea_only_additional_fields": borea_only_fields,
        "numeric_ranges": {
            "basic.damage_multiplier_pct":      [85, 130],
            "basic.status_chance_pct":          [0, 50],
            "basic.status_duration_turns":      [0, 3],
            "basic.cooldown_turns":             [0, 0],
            "basic.target_count":               [1, 1],

            "skill_1.damage_multiplier_pct":    [140, 340],
            "skill_1.healing_multiplier_pct":   [170, 240],
            "skill_1.shield_multiplier_pct":    [170, 240],
            "skill_1.status_chance_pct":        [65, 90],
            "skill_1.status_duration_turns":    [0, 3],
            "skill_1.cooldown_turns":           [3, 3],
            "skill_1.target_count":             [1, 5],

            "skill_2.damage_multiplier_pct":    [220, 520],
            "skill_2.healing_multiplier_pct":   [260, 360],
            "skill_2.shield_multiplier_pct":    [260, 360],
            "skill_2.status_chance_pct":        [70, 95],
            "skill_2.status_duration_turns":    [0, 3],
            "skill_2.cooldown_turns":           [4, 5],
            "skill_2.target_count":             [1, 5],

            "ultimate.damage_multiplier_pct":   [260, 720],
            "ultimate.healing_multiplier_pct":  [380, 520],
            "ultimate.shield_multiplier_pct":   [380, 520],
            "ultimate.status_chance_pct":       [85, 100],
            "ultimate.status_duration_turns":   [0, 3],
            "ultimate.cooldown_turns":          [6, 7],
            "ultimate.target_count":            [1, 5],

            "passive.stat_modifier_pct":        [12, 28],
            "passive.internal_cooldown_turns":  [0, 6],
        },
        "borea_marchio_boreale_draft_ranges": {
            "max_stacks_pvp": [1, 3],
            "max_stacks_pve": [1, 5],
            "damage_bonus_per_stack_pct": [3, 10],
            "freeze_chance_bonus_per_stack_pct": [2, 6],
        },
        "divine_weapon_synergy_rules": {
            "design_only": True,
            "no_runtime_modifier": True,
            "linked_weapon_id_from_entry": True,
            "must_not_apply_numeric_modifier_at_foundation": True,
        },
        "forbidden_fields_per_slot": sorted(FORBIDDEN_FIELDS),
        "safety_rules": {
            "runtime_ready_must_be_false_for_all": True,
            "balance_values_finalized_must_stay_false": True,
            "runtime_attached_must_stay_false": True,
            "battle_runtime_attached_must_stay_false": True,
            "do_not_treat_as_live_kit_must_stay_true": True,
            "ultimate_is_true_ultimate_must_be_true_for_all_13": True,
            "non_ultimate_must_not_be_true_ultimate": True,
            "marchio_boreale_only_on_greek_borea": True,
            "borea_must_remain_hidden_in_api_heroes": True,
            "borea_activation_allowed_must_stay_false": True,
            "no_legacy_borea_hero_id": True,
            "no_primordial_gaia_hero_id_visible": True,
            "no_change_to_descriptions_names_tags_ids": True,
        },
        "is_foundation_pass": True,
        "design_only_field_allowance_note": "divine_weapon_synergy_placeholder and unique_mechanic_placeholder are descriptive design-only sub-objects with runtime_ready=false; they MUST NOT carry numeric runtime modifiers."
    }


# ───────────────────────────── source ────────────────────────────────────
def build_source() -> dict:
    return {
        "source_id": "hero_skill_kits_6star_balance_foundation_source_v1",
        "task_origin": "RM1.32-B",
        "generated_at_utc": NOW_UTC,
        "scope": "6★ heroes only (13). Conservative foundation_draft balance values per slot. NOT runtime. NOT final.",
        "status": "foundation_draft",
        "runtime_ready": False,
        "balance_values_finalized": False,
        "borea_activation": False,
        "include_borea_as_catalog_only": True,
        "entries": [build_source_entry(hid) for hid in ARCHETYPE_OF.keys()],
    }


# ───────────────────────────── patch ─────────────────────────────────────
def backup_catalog() -> Path:
    """Invoke existing backup helper. Return manifest path."""
    res = subprocess.run(
        ['python3', '/app/backend/scripts/backup_hero_skill_kit_catalogs.py',
         '--reason', 'pre-RM1.32-B 6star balance foundation patch'],
        capture_output=True, text=True
    )
    print('--- backup_hero_skill_kit_catalogs.py STDOUT ---')
    print(res.stdout)
    if res.returncode != 0:
        print('--- STDERR ---')
        print(res.stderr)
        raise RuntimeError(f'backup helper failed (exit={res.returncode})')
    # find latest manifest under /app/backups/hero_skill_kits/
    backups_root = Path('/app/backups/hero_skill_kits')
    manifests = sorted(backups_root.glob('*/MANIFEST.json'), key=lambda p: p.stat().st_mtime, reverse=True)
    if not manifests:
        raise RuntimeError('no manifest found after backup')
    return manifests[0]


def patch_catalog(source: dict) -> tuple[str, str]:
    """Patch the 6★ catalog. Returns (sha_before, sha_after)."""
    sha_before = sha256_of(HSK_6STAR)
    c6 = json.loads(HSK_6STAR.read_text(encoding='utf-8'))

    src_by_id = {e['hero_id']: e for e in source['entries']}

    for entry in c6.get('entries', []):
        hid = entry.get('hero_id')
        if hid not in src_by_id:
            raise RuntimeError(f'source missing hero_id {hid}')
        src_slots = src_by_id[hid]['slots']
        pkg = entry.get('skill_package') or {}
        for sn, slot in pkg.items():
            if not isinstance(slot, dict):
                raise RuntimeError(f'{hid}.{sn} not a dict slot')
            if sn not in src_slots:
                raise RuntimeError(f'source missing slot {hid}.{sn}')
            # ONLY mutate final_numbers (currently expected null)
            if slot.get('final_numbers') is not None:
                raise RuntimeError(f'{hid}.{sn}.final_numbers already non-null (drift)')
            slot['final_numbers'] = src_slots[sn]

    # Top-level balance metadata
    c6['balance_pass_id'] = 'RM1.32-B'
    c6['last_balance_foundation_write'] = {
        "task": "RM1.32-B",
        "applied_change": "Added foundation_draft final_numbers blocks on all 78 6★ slots; greek_borea included as catalog-only design data with personal Marchio Boreale draft values; design-only Divine Weapon synergy placeholders added inside final_numbers.",
        "generated_at_utc": NOW_UTC,
        "no_skill_content_change": True,
        "no_slot_change": True,
        "no_status_or_effect_tag_change": True,
        "no_divine_weapon_id_change": True,
        "no_release_group_change": True,
        "no_borea_visibility_change": True,
        "balance_values_finalized": False,
        "runtime_attached": False,
        "battle_runtime_attached": False,
        "runtime_ready": False,
        "borea_activation": False,
        "do_not_treat_as_live_kit": True,
    }
    # Confirm top-level safety flags remain false / true as required
    c6['runtime_attached'] = False
    c6['battle_runtime_attached'] = False
    c6['balance_values_finalized'] = False
    c6['do_not_treat_as_live_kit'] = True

    # Write (compact + stable key ordering as it was)
    HSK_6STAR.write_text(json.dumps(c6, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    sha_after = sha256_of(HSK_6STAR)
    return sha_before, sha_after


# ───────────────────────────── main ──────────────────────────────────────
def main() -> int:
    # 1. backup
    print('[1/4] Backup pre-patch …')
    manifest = backup_catalog()
    print(f'      Manifest: {manifest}')

    # 2. contract + source
    print('[2/4] Build contract + source …')
    contract = build_contract()
    source = build_source()
    CONTRACT_OUT.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    SOURCE_OUT.write_text(json.dumps(source, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'      Contract: {CONTRACT_OUT}')
    print(f'      Source  : {SOURCE_OUT}')

    # 3. patch catalog
    print('[3/4] Patch 6★ catalog …')
    sha_before, sha_after = patch_catalog(source)
    print(f'      SHA before: {sha_before}')
    print(f'      SHA after : {sha_after}')

    # 4. summary
    print('[4/4] Summary')
    c6 = json.loads(HSK_6STAR.read_text(encoding='utf-8'))
    entries = c6.get('entries', [])
    total_fn = 0
    ult_true = 0
    for e in entries:
        for sn, slot in (e.get('skill_package') or {}).items():
            if isinstance(slot, dict) and isinstance(slot.get('final_numbers'), dict):
                total_fn += 1
                if sn == 'ultimate' and slot['final_numbers'].get('is_true_ultimate') is True:
                    ult_true += 1
    print(f'      6★ entries           : {len(entries)}')
    print(f'      final_numbers objects: {total_fn}/78')
    print(f'      ultimate is_true_ultimate=true: {ult_true}/13')
    print(f'      Manifest path        : {manifest}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
