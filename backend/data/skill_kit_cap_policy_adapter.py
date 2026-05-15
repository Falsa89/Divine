"""
RM1.33-A — Skill Kit Cap Policy Adapter (READ-ONLY, INERT)
──────────────────────────────────────────────────────────────────────
Reads the design-only delta plan from RM1.32-C:
  /app/data/design/hero_skill_kits/hero_skill_kits_balance_cap_delta_plan_v1.json

Produces normalized cap policy descriptors for `pvp`, `boss`, and `pve`
contexts as **preview/debug** data only. NEVER applies anything to live
combat.

All outputs carry the safety markers:
  - runtime_attached = False
  - battle_runtime_attached = False
  - applied_to_combat = False
  - preview_only = True

The future runtime adapter will pair these descriptors with the skill
kit normalized data ONLY when SKILL_KIT_RUNTIME_ENABLED is flipped to the
exact truthy allowlist token.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from backend.data.skill_kit_runtime_adapter import (  # noqa: F401
    is_skill_kit_runtime_enabled,
)  # imported for cross-reference / sanity

_DELTA_PLAN_PATH = Path('/app/data/design/hero_skill_kits/hero_skill_kits_balance_cap_delta_plan_v1.json')
_VALID_CONTEXTS = {'pvp', 'boss', 'pve'}


def load_balance_cap_delta_plan() -> dict[str, Any]:
    """Read-only load of the RM1.32-C delta plan. Returns a dict.

    Adds a wrapper indicating preview-only nature. Does NOT mutate the JSON.
    """
    plan = json.loads(_DELTA_PLAN_PATH.read_text(encoding='utf-8'))
    return {
        'plan_id': plan.get('plan_id'),
        'task_origin': plan.get('task_origin'),
        'patch_applied': plan.get('patch_applied', False),
        'safety_flags': plan.get('safety_flags', {}),
        'pvp_cap_recommendations': plan.get('pvp_cap_recommendations', {}),
        'boss_resistance_recommendations': plan.get('boss_resistance_recommendations', {}),
        'domain_recommendations': plan.get('domain_recommendations', {}),
        'marchio_boreale_recommendations': plan.get('marchio_boreale_recommendations', {}),
        'divine_weapon_synergy_recommendations': plan.get('divine_weapon_synergy_recommendations', {}),
        'heal_shield_revive_recommendations': plan.get('heal_shield_revive_recommendations', {}),
        'preview_only': True,
        'applied_to_combat': False,
        'runtime_attached': False,
        'battle_runtime_attached': False,
    }


def _disabled_policy(context: str, reason: str) -> dict[str, Any]:
    return {
        'enabled': False,
        'context': context,
        'reason': reason,
        'feature_flag_value': bool(is_skill_kit_runtime_enabled()),
        'preview_only': True,
        'applied_to_combat': False,
        'runtime_attached': False,
        'battle_runtime_attached': False,
        'policy': None,
    }


def get_cap_policy_for_context(context: str = 'pvp') -> dict[str, Any]:
    """Return the normalized cap policy for one of `pvp` | `boss` | `pve`.

    Output is preview/debug ONLY. Always carries `applied_to_combat=False`
    and `runtime_attached=False`. Does not mutate any state.
    """
    if context not in _VALID_CONTEXTS:
        return _disabled_policy(context, 'invalid_context')
    plan = load_balance_cap_delta_plan()

    pvp = plan.get('pvp_cap_recommendations') or {}
    boss = plan.get('boss_resistance_recommendations') or {}
    marchio = plan.get('marchio_boreale_recommendations') or {}
    dw = plan.get('divine_weapon_synergy_recommendations') or {}
    domain = plan.get('domain_recommendations') or {}
    hsr = plan.get('heal_shield_revive_recommendations') or {}

    if context == 'pvp':
        policy = {
            'damage_cap_single_target_pct_max': 600,
            'damage_cap_aoe_per_target_pct_max': 380,
            'shield_effective_cap_pct': 460,
            'shield_concurrent_max_per_ally': 2,
            'heal_effectiveness_multiplier': 0.75,
            'hard_control_duration_turns_max': 2,
            'status_chance_pct_max': 85,
            'marchio_boreale_max_stacks': marchio.get('max_stacks_pvp', 3),
            'dw_synergy_numeric_modifier_pct_max': 5,
            'one_shot_prevention_pct_floor': 10,
            'enforcement_layer': 'future_runtime_adapter_RM1.33+',
        }
    elif context == 'boss':
        policy = {
            'hard_control_diminishing_returns': {
                'first_application_duration_factor': 1.0,
                'second_application_window_factor': 0.5,
                'third_application_immune': True,
                'immunity_window_turns': 2,
            },
            'dot_tick_multiplier_cap': 0.5,
            'dot_no_crit_on_boss': True,
            'max_distinct_dot_pve': 3,
            'max_distinct_dot_pvp': 2,
            'healing_block_max_turns': 2,
            'healing_reduction_per_stack_max_pct': -60,
            'healing_reduction_min_floor_pct': 20,
            'marchio_boreale_effective_cap_on_boss': 4,
            'marchio_freeze_bonus_on_boss_factor': 0.5,
            'mark_stack_cap_pve': 5,
            'mark_stack_cap_pvp': 3,
            'enforcement_layer': 'future_runtime_adapter_RM1.33+',
        }
    else:  # 'pve'
        policy = {
            'damage_cap_single_target_pct_max': None,  # unrestricted vs trash
            'damage_cap_aoe_per_target_pct_max': None,
            'shield_effective_cap_pct': None,
            'shield_concurrent_max_per_ally': 3,
            'heal_effectiveness_multiplier': 1.0,
            'hard_control_duration_turns_max': 3,
            'status_chance_pct_max': 100,
            'marchio_boreale_max_stacks': marchio.get('max_stacks_pve', 5),
            'dw_synergy_numeric_modifier_pct_max': 10,
            'revive_per_ally_max': 1,
            'enforcement_layer': 'future_runtime_adapter_RM1.33+',
        }

    # Add cross-context descriptors
    policy['marchio_boreale_team_wide_amp_allowed'] = False
    policy['marchio_owner_hero_id'] = marchio.get('owner_hero_id', 'greek_borea')
    policy['domain_policy'] = {
        'stacking_policy': domain.get('stacking_policy', 'one_domain_active_per_battle_side'),
        'override_policy': domain.get('override_policy', 'strongest_wins'),
        'duration_policy': domain.get('duration_policy', 'max 3 turns; no same-turn refresh'),
    }
    policy['dw_synergy_rules'] = {
        'numeric_modifier_pct_global_cap': dw.get('future_runtime_caps', {}).get('max_numeric_modifier_pct', 10),
        'pvp_cap_pct': 5,
        'per_owner_only': True,
        'additive_only_at_first_runtime_pass': True,
    }
    policy['revive_anti_loop_rule'] = hsr.get('revive_anti_loop_rule', 'max 1 revive per ally per battle')

    return {
        'enabled': False,            # never enabled in RM1.33-A
        'context': context,
        'plan_id': plan.get('plan_id'),
        'preview_only': True,
        'applied_to_combat': False,
        'runtime_attached': False,
        'battle_runtime_attached': False,
        'feature_flag_value': bool(is_skill_kit_runtime_enabled()),
        'policy': policy,
    }


def preview_cap_policy_for_skill(hero_id: str, slot: str, context: str = 'pvp') -> dict[str, Any]:
    """Preview helper: returns the cap policy for `context` annotated with
    the hero/slot. Pure function. NEVER applies to combat.
    """
    policy = get_cap_policy_for_context(context)
    return {
        'hero_id': hero_id,
        'slot': slot,
        'context': context,
        'preview_only': True,
        'applied_to_combat': False,
        'runtime_attached': False,
        'battle_runtime_attached': False,
        'cap_policy': policy,
    }


CAP_POLICY_MANIFEST: dict[str, Any] = {
    'adapter_id': 'skill_kit_cap_policy_adapter_rm133a',
    'task_origin': 'RM1.33-A',
    'reads_delta_plan': str(_DELTA_PLAN_PATH),
    'writes_to_catalogs': False,
    'writes_to_db': False,
    'writes_to_runtime': False,
    'applied_to_combat': False,
    'contexts_supported': sorted(_VALID_CONTEXTS),
    'imported_by_battle_engine': False,
    'imported_by_combat_tsx': False,
}
