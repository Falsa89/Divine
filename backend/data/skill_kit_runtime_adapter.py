"""
RM1.33-A — Skill Kit Runtime Adapter (SKELETON, OFF BY DEFAULT)
──────────────────────────────────────────────────────────────────────
Read-only adapter skeleton that prepares the future bridge between the
Hero Skill Kit Catalog (5★/6★ foundation_draft) and the battle runtime.

ABSOLUTE RULE: SKILL_KIT_RUNTIME_ENABLED is **OFF** by default and this
module MUST NEVER alter live combat behavior at this stage.

  - Pure functions only.
  - No writes (catalog/DB/runtime/gacha/roster).
  - No imports inside `battle_engine.py` that would alter output.
  - When the flag is OFF, every runtime-facing function returns a safe
    `disabled` result object — NEVER a live numeric payload.

The flag is intentionally non-overridable via env-only truthy strings:
it must be exactly equal to one of the allowlisted truthy tokens.
Default is `false`.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Feature flag
# ---------------------------------------------------------------------------

_ENV_VAR = "SKILL_KIT_RUNTIME_ENABLED"
# Strict allowlist. Anything else → OFF. Default → OFF.
_TRUTHY_ALLOWLIST = frozenset({"true_explicit_runtime_on"})


def is_skill_kit_runtime_enabled() -> bool:
    """Return True only if the env var EXACTLY matches the allowlisted token.

    Default OFF. Missing env → False. Any unexpected value → False.
    NEVER set to True in RM1.33-A.
    """
    val = os.environ.get(_ENV_VAR, "")
    return val in _TRUTHY_ALLOWLIST


# ---------------------------------------------------------------------------
# Catalog source paths (READ-ONLY)
# ---------------------------------------------------------------------------

_HSK_5STAR = Path('/app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json')
_HSK_6STAR = Path('/app/data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json')

_VALID_5STAR_SLOTS = {'basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2'}
_VALID_6STAR_SLOTS = {'basic', 'passive_base', 'skill_1', 'passive_advanced', 'skill_2', 'ultimate'}
_FORBIDDEN_HERO_IDS = {'borea', 'primordial_gaia', 'greek_boreas', 'olympian_borea'}


def _read_json(p: Path) -> dict[str, Any]:
    return json.loads(p.read_text(encoding='utf-8'))


def _entries_by_id(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {e.get('hero_id'): e for e in (catalog.get('entries') or []) if isinstance(e, dict)}


# ---------------------------------------------------------------------------
# Disabled / fallback result helper
# ---------------------------------------------------------------------------

def get_disabled_runtime_result(hero_id: str, slot: str | None, reason: str) -> dict[str, Any]:
    """Return the canonical safe payload returned when runtime is disabled.

    The returned shape is fixed and contains NO numeric live values. It is
    safe to log, return through an API for debug, or pass through the
    skeleton without ever being used as a runtime damage/heal/status source.
    """
    return {
        'enabled': False,
        'runtime_attached': False,
        'battle_runtime_attached': False,
        'hero_id': hero_id,
        'slot': slot,
        'reason': reason,
        'feature_flag': _ENV_VAR,
        'feature_flag_value': bool(is_skill_kit_runtime_enabled()),
        'payload': None,
        'is_disabled_runtime_result': True,
    }


# ---------------------------------------------------------------------------
# Pure read-path / normalization functions (always safe to call)
# ---------------------------------------------------------------------------

def load_skill_kit_for_hero(hero_id: str) -> dict[str, Any]:
    """Read-only loader. Returns the catalog entry for `hero_id`.

    NEVER mutates anything. Returns a `disabled` payload for forbidden
    legacy hero_ids. For valid hero_ids not in 5★/6★, returns disabled
    payload with reason='not_in_catalog'.
    """
    if not isinstance(hero_id, str) or not hero_id:
        return get_disabled_runtime_result(hero_id, None, 'invalid_hero_id')
    if hero_id in _FORBIDDEN_HERO_IDS:
        return get_disabled_runtime_result(hero_id, None, 'forbidden_legacy_hero_id')
    try:
        c5 = _read_json(_HSK_5STAR)
        c6 = _read_json(_HSK_6STAR)
    except Exception as e:  # pragma: no cover - defensive
        return get_disabled_runtime_result(hero_id, None, f'catalog_io_error:{e!r}')
    e5 = _entries_by_id(c5)
    e6 = _entries_by_id(c6)
    if hero_id in e5:
        return {'present': True, 'rarity': '5star', 'entry': e5[hero_id]}
    if hero_id in e6:
        return {'present': True, 'rarity': '6star', 'entry': e6[hero_id]}
    return get_disabled_runtime_result(hero_id, None, 'not_in_catalog')


def normalize_skill_slot(hero_id: str, slot: str) -> dict[str, Any]:
    """Pure function. Returns a normalized, read-only descriptor of the slot.

    Output is a small, JSON-safe dict. It carries NO live runtime power.
    It is suitable for debug/preview only.
    """
    kit = load_skill_kit_for_hero(hero_id)
    if not kit.get('present'):
        return get_disabled_runtime_result(hero_id, slot, kit.get('reason', 'unknown'))
    rarity = kit['rarity']
    valid = _VALID_5STAR_SLOTS if rarity == '5star' else _VALID_6STAR_SLOTS
    if slot not in valid:
        return get_disabled_runtime_result(hero_id, slot, f'invalid_slot_for_{rarity}')
    slot_obj = (kit['entry'].get('skill_package') or {}).get(slot)
    if not isinstance(slot_obj, dict):
        return get_disabled_runtime_result(hero_id, slot, 'slot_missing')
    fn = slot_obj.get('final_numbers')
    fn_dict = fn if isinstance(fn, dict) else {}
    return {
        'hero_id': hero_id,
        'rarity': rarity,
        'slot': slot,
        'display_name': slot_obj.get('display_name'),
        'skill_type': slot_obj.get('skill_type'),
        'element': slot_obj.get('element'),
        'targeting_intent': slot_obj.get('targeting_intent'),
        'core_status_ids': list(slot_obj.get('core_status_ids') or []),
        'core_effect_tags': list(slot_obj.get('core_effect_tags') or []),
        # NORMALIZED descriptor of final_numbers — still inert / for preview only
        'final_numbers_meta': {
            'status': fn_dict.get('status'),
            'runtime_ready': fn_dict.get('runtime_ready', False),
            'scaling_stat': fn_dict.get('scaling_stat'),
            'effect_strength_tier': fn_dict.get('effect_strength_tier'),
            'cooldown_turns': fn_dict.get('cooldown_turns'),
            'target_count': fn_dict.get('target_count'),
            'is_true_ultimate': fn_dict.get('is_true_ultimate', False),
            # numeric values are echoed for *preview/debug* only; flag below
            'preview_values': {
                'damage_multiplier_pct': fn_dict.get('damage_multiplier_pct'),
                'healing_multiplier_pct': fn_dict.get('healing_multiplier_pct'),
                'shield_multiplier_pct': fn_dict.get('shield_multiplier_pct'),
                'status_chance_pct': fn_dict.get('status_chance_pct'),
                'status_duration_turns': fn_dict.get('status_duration_turns'),
                'stat_modifier_pct': fn_dict.get('stat_modifier_pct'),
                'internal_cooldown_turns': fn_dict.get('internal_cooldown_turns'),
            },
            'preview_only': True,
            'design_only': True,
            'do_not_treat_as_live_kit': True,
        },
        'runtime_attached': False,
        'battle_runtime_attached': False,
    }


def get_skill_runtime_candidate(hero_id: str, slot: str) -> dict[str, Any]:
    """Runtime-facing function. ALWAYS returns the disabled payload when
    the feature flag is OFF.

    When the flag becomes ON (NOT in RM1.33-A), this is the entry point a
    future battle engine adapter will call to obtain a runtime candidate.
    Until then, this function is a guarded façade.
    """
    if not is_skill_kit_runtime_enabled():
        return get_disabled_runtime_result(hero_id, slot, 'feature_flag_off')
    # If/when enabled, the future implementation will compose the
    # normalized slot with the cap policy adapter. We deliberately leave
    # this branch as a NotImplemented sentinel to forbid accidental hooks.
    return get_disabled_runtime_result(hero_id, slot, 'runtime_path_not_implemented_in_rm133a')


# ---------------------------------------------------------------------------
# Adapter manifest — useful for the safety audit & docs
# ---------------------------------------------------------------------------

ADAPTER_MANIFEST: dict[str, Any] = {
    'adapter_id': 'skill_kit_runtime_adapter_rm133a',
    'task_origin': 'RM1.33-A',
    'feature_flag_env_var': _ENV_VAR,
    'default_state': 'off',
    'truthy_allowlist': sorted(_TRUTHY_ALLOWLIST),
    'pure_functions': [
        'is_skill_kit_runtime_enabled',
        'load_skill_kit_for_hero',
        'normalize_skill_slot',
        'get_skill_runtime_candidate',
        'get_disabled_runtime_result',
    ],
    'writes_to_db': False,
    'writes_to_catalogs': False,
    'writes_to_runtime': False,
    'imported_by_battle_engine': False,
    'imported_by_combat_tsx': False,
}
