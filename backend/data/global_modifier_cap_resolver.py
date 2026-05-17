"""
STACK-B — Global Modifier Cap Resolver (SKELETON, OFF BY DEFAULT)
─────────────────────────────────────────────────────────────────
Inert global cap resolver skeleton that will eventually clamp combined
additive modifiers across Collection Synergy V2, Affinity Phase 2,
Divine Weapons, Skill Kit foundations, and Boss interactions.

ABSOLUTE RULES:
  - This module MUST NEVER be imported by `battle_engine.py`,
    `battle_core.py`, or `combat.tsx`.
  - `GLOBAL_MODIFIER_CAP_RESOLVER_ENABLED` is OFF by default and the
    only truthy token allowlisted is the explicit string
    `true_explicit_global_cap_runtime_on`. This task MUST NOT set it.
  - All runtime-facing entry points return an inert `disabled` payload
    carrying NO live numeric cap result. The only thing returned today
    is a documentation-grade preview echoing what the cap policy WOULD
    be once approved.
  - No DB writes. No catalog mutations. No Borea activation.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Feature flag (strictly OFF)
# ---------------------------------------------------------------------------

_ENV_VAR = "GLOBAL_MODIFIER_CAP_RESOLVER_ENABLED"
_TRUTHY_ALLOWLIST = frozenset({"true_explicit_global_cap_runtime_on"})


def is_global_modifier_cap_resolver_enabled() -> bool:
    """Return True only if env var EXACTLY equals the allowlisted token."""
    val = os.environ.get(_ENV_VAR, "")
    return val in _TRUTHY_ALLOWLIST


# ---------------------------------------------------------------------------
# Source files (READ-ONLY)
# ---------------------------------------------------------------------------

_STACK_REPORT = Path(
    '/app/data/design/system_safety/'
    'cross_system_progression_stack_safety_report_v1.json'
)


def _read_json_safe(p: Path) -> dict[str, Any] | None:
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Disabled / inert result helper
# ---------------------------------------------------------------------------

def get_disabled_global_cap_result(reason: str = "feature_flag_off") -> dict[str, Any]:
    """Canonical safe payload when the global cap resolver is OFF.

    Fixed shape, no live numeric cap, safe to log or expose via an inert
    debug surface.
    """
    return {
        'enabled': False,
        'runtime_attached': False,
        'battle_runtime_attached': False,
        'applied_to_combat': False,
        'db_write': False,
        'reason': reason,
        'feature_flag': _ENV_VAR,
        'feature_flag_value': bool(is_global_modifier_cap_resolver_enabled()),
        'payload': None,
        'is_disabled_global_cap_result': True,
    }


# ---------------------------------------------------------------------------
# Cap principles (documentation grade only, never applied to combat)
# ---------------------------------------------------------------------------

CAP_PRINCIPLES: dict[str, Any] = {
    'no_multiplicative_stacking_initially': True,
    'stacking_rule': 'additive_capped',
    'collection_total_cap_pct': 15,
    'collection_per_category_cap_pct': 5,
    'affinity_pvp_per_source_cap_pct': 2,
    'affinity_pvp_total_cap_pct': 6,
    'divine_weapon_global_cap_pct_future': 10,
    'divine_weapon_pvp_cap_pct_future': 5,
    'skill_kit_foundation_runtime_attached': False,
    'boss_policies_design_only': True,
    'combined_future_pvp_total_cap_pct_max_recommended': 12,
    'pvp_combined_future_cap_requires_explicit_approval': True,
}


# ---------------------------------------------------------------------------
# Pure preview functions (always safe to call; never live)
# ---------------------------------------------------------------------------

def preview_stack_policy() -> dict[str, Any]:
    """Return the inert stack policy + cap principles. Never live."""
    report = _read_json_safe(_STACK_REPORT)
    return {
        'enabled': False,
        'runtime_attached': False,
        'applied_to_combat': False,
        'db_write': False,
        'preview_only': True,
        'design_only': True,
        'stack_report_anchor': (report or {}).get('report_id', 'stack_report_missing'),
        'cap_principles': dict(CAP_PRINCIPLES),
        'feature_flag': _ENV_VAR,
        'feature_flag_value': bool(is_global_modifier_cap_resolver_enabled()),
    }


def preview_cap_sources() -> dict[str, Any]:
    """Return the list of sources that the future resolver would consider.

    No live values; documentation-grade only.
    """
    return {
        'enabled': False,
        'runtime_attached': False,
        'applied_to_combat': False,
        'db_write': False,
        'preview_only': True,
        'design_only': True,
        'sources': [
            {
                'id': 'collection_synergy_v2',
                'state': 'inert',
                'feature_flag': 'COLLECTION_SYNERGY_BATTLE_ENABLED',
                'cap_per_category_pct': CAP_PRINCIPLES['collection_per_category_cap_pct'],
                'cap_total_pct': CAP_PRINCIPLES['collection_total_cap_pct'],
            },
            {
                'id': 'affinity_phase_2',
                'state': 'inert',
                'feature_flag': 'AFFINITY_GIFT_RUNTIME_ENABLED',
                'cap_per_source_pct_pvp': CAP_PRINCIPLES['affinity_pvp_per_source_cap_pct'],
                'cap_total_pct_pvp': CAP_PRINCIPLES['affinity_pvp_total_cap_pct'],
            },
            {
                'id': 'divine_weapons',
                'state': 'catalog_only',
                'feature_flag': 'DW_RUNTIME_ENABLED_FUTURE',
                'cap_global_pct_future': CAP_PRINCIPLES['divine_weapon_global_cap_pct_future'],
                'cap_pvp_pct_future': CAP_PRINCIPLES['divine_weapon_pvp_cap_pct_future'],
            },
            {
                'id': 'skill_kit_foundation',
                'state': 'inert_adapter_off',
                'feature_flag': 'SKILL_KIT_RUNTIME_ENABLED',
            },
            {
                'id': 'boss_policies',
                'state': 'design_only',
                'feature_flag': None,
            },
        ],
        'feature_flag': _ENV_VAR,
        'feature_flag_value': bool(is_global_modifier_cap_resolver_enabled()),
    }


def preview_combined_cap(
    mock_sources: list[dict[str, Any]] | None = None,
    context: str = "pvp",
) -> dict[str, Any]:
    """Inert preview of what the combined cap WOULD return.

    Never returns a live applied buff. If the resolver is OFF (always in
    STACK-B), it returns the disabled envelope augmented with a
    documentation-grade clamped_pct echo computed in-memory from
    `mock_sources`.

    Args:
      mock_sources: list of {id, pct} dicts. Optional.
      context: "pvp" or "pve" (documentation hint only).
    """
    sources = list(mock_sources or [])
    # STACK-D: multiplicative sources rejected (excluded from additive sum).
    # STACK-E: Borea-locked sources filtered (excluded from additive sum).
    # STACK-F: debuff (negative pct) sources tracked separately and clamped,
    #          NEVER converted to buffs even if their absolute value would
    #          push under the cap.
    BOREA_TOKENS = {'borea', 'primordial_gaia', 'greek_borea'}
    DEBUFF_FLOOR_PCT = -50  # documentation-grade clamp floor (never live)

    cleaned: list[dict[str, Any]] = []
    debuffs: list[dict[str, Any]] = []
    rejected_multiplicative: list[dict[str, Any]] = []
    filtered_borea_locked: list[dict[str, Any]] = []
    for s in sources:
        if not isinstance(s, dict):
            continue
        pct = s.get('pct')
        if not isinstance(pct, (int, float)):
            continue
        pct_f = float(pct)
        # Multiplicative detection (STACK-D)
        mode = s.get('stacking_mode') or s.get('stacking')
        if isinstance(mode, str) and mode.strip().lower() == 'multiplicative':
            rejected_multiplicative.append({
                'id': s.get('id'),
                'pct': pct_f,
                'stacking_mode': mode,
                'reason': 'multiplicative_rejected_preview_only',
                'forbidden_in_initial_runtime': True,
            })
            continue
        # Borea filter (STACK-E): explicit borea_locked field OR id/source
        # contains a Borea token. Filtered BEFORE additive accumulation.
        sid_low = str(s.get('id') or '').lower()
        src_low = str(s.get('source') or '').lower()
        is_borea = bool(s.get('borea_locked')) or any(
            tok in sid_low or tok in src_low for tok in BOREA_TOKENS
        )
        if is_borea:
            filtered_borea_locked.append({
                'id': s.get('id'),
                'pct': pct_f,
                'reason': 'borea_locked_preview_filter',
                'rule': 'no_hidden_hero_contribution',
                'forbidden_in_initial_runtime': True,
            })
            continue
        # Debuff detection (STACK-F): negative pct tracked separately,
        # clamped at DEBUFF_FLOOR_PCT, NEVER converted to a buff.
        if pct_f < 0:
            clamped_debuff = max(pct_f, float(DEBUFF_FLOOR_PCT))
            debuffs.append({
                'id': s.get('id'),
                'pct': pct_f,
                'clamped_pct': clamped_debuff,
                'rule': 'debuff_preview_no_buff_conversion',
                'never_converted_to_buff': True,
                'floor_pct': DEBUFF_FLOOR_PCT,
            })
            continue
        cleaned.append({
            'id': s.get('id'),
            'pct': pct_f,
            'stacking_mode': 'additive',
        })

    additive_sum = sum(s['pct'] for s in cleaned)
    debuff_sum = sum(d['clamped_pct'] for d in debuffs)
    if context == 'pvp':
        target_cap = CAP_PRINCIPLES['combined_future_pvp_total_cap_pct_max_recommended']
    else:
        # PvE intentionally has no combined cap today (per stack report)
        target_cap = None
    clamped_pct_preview = (
        min(additive_sum, target_cap) if target_cap is not None else additive_sum
    )

    base = get_disabled_global_cap_result(reason='feature_flag_off')
    base.update({
        'preview_only': True,
        'design_only': True,
        'context': context,
        'mock_sources_input': cleaned,
        'mock_sources_rejected_multiplicative': rejected_multiplicative,
        'multiplicative_rejected_count': len(rejected_multiplicative),
        'multiplicative_policy': 'rejected_preview_only',
        'multiplicative_forbidden_in_initial_runtime': True,
        # STACK-E
        'mock_sources_filtered_borea_locked': filtered_borea_locked,
        'borea_locked_filtered_count': len(filtered_borea_locked),
        'borea_filter_policy': 'no_hidden_hero_contribution_preview_filter',
        'borea_forbidden_in_initial_runtime': True,
        # STACK-F
        'mock_sources_debuffs': debuffs,
        'debuff_count': len(debuffs),
        'debuff_sum_pct_preview': debuff_sum,
        'debuff_floor_pct': DEBUFF_FLOOR_PCT,
        'debuff_policy': 'tracked_separately_clamped_never_converted_to_buff',
        'debuff_never_converted_to_buff': True,
        'additive_sum_pct_preview': additive_sum,
        'target_cap_pct_preview': target_cap,
        'clamped_pct_preview': clamped_pct_preview,
        'note': (
            'preview_only: the resolver is OFF; this echo is documentation-grade only '
            'and is NEVER applied to combat. Multiplicative-stacking sources, '
            'Borea-locked sources, and debuffs (negative pct) are reported in '
            'separate buckets and excluded from the additive_sum_pct_preview.'
        ),
    })
    return base


# ---------------------------------------------------------------------------
# Adapter manifest
# ---------------------------------------------------------------------------

ADAPTER_MANIFEST: dict[str, Any] = {
    'adapter_id': 'global_modifier_cap_resolver_stack_b',
    'task_origin': 'STACK-B',
    'feature_flag_env_var': _ENV_VAR,
    'default_state': 'off',
    'truthy_allowlist': sorted(_TRUTHY_ALLOWLIST),
    'pure_functions': [
        'is_global_modifier_cap_resolver_enabled',
        'preview_stack_policy',
        'preview_cap_sources',
        'preview_combined_cap',
        'get_disabled_global_cap_result',
    ],
    'writes_to_db': False,
    'writes_to_catalogs': False,
    'writes_to_runtime': False,
    'imported_by_battle_engine': False,
    'imported_by_battle_core': False,
    'imported_by_combat_tsx': False,
    'applied_to_combat': False,
    'no_borea_activation': True,
    'cap_principles': dict(CAP_PRINCIPLES),
}
