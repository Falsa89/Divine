"""
CS2-B — Collection Synergy V2 Preview Resolver (SKELETON, OFF BY DEFAULT)
──────────────────────────────────────────────────────────────────────
Read-only / inert skeleton that prepares the future bridge between the
Collection Synergy V2 readiness drafts and a possible future runtime.

ABSOLUTE RULES:
  - This module MUST NEVER be imported by `battle_engine.py` or
    `combat.tsx`. It is design-only / preview-only.
  - `COLLECTION_SYNERGY_BATTLE_ENABLED` is OFF by default and the only
    truthy token allowlisted is the explicit string
    `true_explicit_collection_runtime_on`. This task MUST NOT set it.
  - All runtime-facing entry points return an inert `disabled` payload
    that carries NO live numeric buff and NO live combat side effect.
  - No DB writes. No catalog mutations. No Borea activation.

Mirrors the contract pattern of `skill_kit_runtime_adapter.py` (RM1.33-A)
but for the Collection Synergy V2 preview surface.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Feature flag (strictly OFF)
# ---------------------------------------------------------------------------

_ENV_VAR = "COLLECTION_SYNERGY_BATTLE_ENABLED"
_TRUTHY_ALLOWLIST = frozenset({"true_explicit_collection_runtime_on"})


def is_collection_synergy_runtime_enabled() -> bool:
    """Return True only if the env var equals EXACTLY the allowlisted token.

    Default OFF. Missing env -> False. Any common truthy variant
    (true/1/yes/on/TRUE) -> False. MUST stay False in CS2-B.
    """
    val = os.environ.get(_ENV_VAR, "")
    return val in _TRUTHY_ALLOWLIST


# ---------------------------------------------------------------------------
# Source files (READ-ONLY)
# ---------------------------------------------------------------------------

_READINESS_PLAN = Path(
    '/app/data/design/synergies/collection_synergies_v2_readiness_plan_v1.json'
)
_SCHEMA_DRAFT = Path(
    '/app/data/design/synergies/collection_synergy_v2_schema_draft_v1.json'
)

_FORBIDDEN_HERO_IDS = {'borea', 'primordial_gaia', 'greek_boreas', 'olympian_borea'}


def _read_json(p: Path) -> dict[str, Any]:
    return json.loads(p.read_text(encoding='utf-8'))


# ---------------------------------------------------------------------------
# Disabled / inert result helper
# ---------------------------------------------------------------------------

def get_disabled_collection_runtime_result(reason: str = "feature_flag_off") -> dict[str, Any]:
    """Canonical safe payload when the collection synergy runtime is OFF.

    Fixed shape, no live numeric payload, safe to log or expose via a
    future inert debug endpoint.
    """
    return {
        'enabled': False,
        'runtime_attached': False,
        'battle_runtime_attached': False,
        'applied_to_combat': False,
        'db_write': False,
        'reason': reason,
        'feature_flag': _ENV_VAR,
        'feature_flag_value': bool(is_collection_synergy_runtime_enabled()),
        'payload': None,
        'is_disabled_collection_runtime_result': True,
    }


# ---------------------------------------------------------------------------
# Pure read-path / preview functions (always safe to call)
# ---------------------------------------------------------------------------

def load_collection_synergy_readiness() -> dict[str, Any]:
    """Read the CS2-A readiness plan. Returns a disabled payload on IO error."""
    try:
        return _read_json(_READINESS_PLAN)
    except Exception as e:  # pragma: no cover - defensive
        return get_disabled_collection_runtime_result(
            reason=f'readiness_plan_io_error:{e!r}'
        )


def load_collection_synergy_schema_draft() -> dict[str, Any]:
    """Read the CS2-A schema draft (if present)."""
    if not _SCHEMA_DRAFT.exists():
        return get_disabled_collection_runtime_result(reason='schema_draft_missing')
    try:
        return _read_json(_SCHEMA_DRAFT)
    except Exception as e:  # pragma: no cover - defensive
        return get_disabled_collection_runtime_result(
            reason=f'schema_draft_io_error:{e!r}'
        )


def preview_collection_synergy_categories() -> dict[str, Any]:
    """Return the inert category list documented in the CS2-A plan.

    Output is a JSON-safe dict carrying NO live buff. Suitable for
    preview / debug only.
    """
    plan = load_collection_synergy_readiness()
    if plan.get('is_disabled_collection_runtime_result'):
        return plan
    cats = plan.get('proposed_collection_synergy_categories') or []
    return {
        'enabled': False,
        'runtime_attached': False,
        'battle_runtime_attached': False,
        'applied_to_combat': False,
        'db_write': False,
        'preview_only': True,
        'design_only': True,
        'count': len(cats),
        'categories': [
            {
                'id': c.get('id'),
                'description': c.get('description'),
                'axis': c.get('axis'),
                'future_runtime_feature_flag': c.get('future_runtime_feature_flag'),
            }
            for c in cats if isinstance(c, dict)
        ],
        'feature_flag': _ENV_VAR,
        'feature_flag_value': bool(is_collection_synergy_runtime_enabled()),
    }


def preview_collection_milestone_policy() -> dict[str, Any]:
    """Return the inert milestone / cap model documented in the CS2-A plan.

    No live values are emitted. Caps are echoed for documentation only.
    """
    plan = load_collection_synergy_readiness()
    if plan.get('is_disabled_collection_runtime_result'):
        return plan
    model = plan.get('proposed_milestone_model') or {}
    return {
        'enabled': False,
        'runtime_attached': False,
        'battle_runtime_attached': False,
        'applied_to_combat': False,
        'db_write': False,
        'preview_only': True,
        'design_only': True,
        'milestone_model': {
            'trigger_axis': model.get('trigger_axis'),
            'owned_count_thresholds_tiered': list(
                model.get('owned_count_thresholds_tiered') or []
            ),
            'star_threshold_future_optional': list(
                model.get('star_threshold_future_optional') or []
            ),
            'max_total_collection_bonus_pct': model.get('max_total_collection_bonus_pct'),
            'max_per_category_bonus_pct': model.get('max_per_category_bonus_pct'),
            'stacking_rule': model.get('stacking_rule'),
            'applies_to': list(model.get('applies_to') or []),
        },
        'feature_flag': _ENV_VAR,
        'feature_flag_value': bool(is_collection_synergy_runtime_enabled()),
    }


def preview_collection_synergy_for_mock_roster(
    mock_hero_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Return a strictly inert preview for a mock roster of hero ids.

    Always returns an inert disabled-like envelope. NEVER computes a
    real buff. Forbidden hero ids (borea, primordial_gaia) are filtered
    from the echoed roster.
    """
    if mock_hero_ids is None:
        mock_hero_ids = []
    safe_roster = [h for h in mock_hero_ids if isinstance(h, str) and h not in _FORBIDDEN_HERO_IDS]
    filtered_out = [h for h in mock_hero_ids if isinstance(h, str) and h in _FORBIDDEN_HERO_IDS]
    return {
        'enabled': False,
        'runtime_attached': False,
        'battle_runtime_attached': False,
        'applied_to_combat': False,
        'db_write': False,
        'preview_only': True,
        'design_only': True,
        'mock_roster_input_count': len(mock_hero_ids),
        'mock_roster_used_count': len(safe_roster),
        'mock_roster': safe_roster,
        'forbidden_filtered_out': filtered_out,
        'computed_buffs': None,
        'note': 'Live collection synergy resolution is disabled. This preview never returns numeric buffs.',
        'reason': 'feature_flag_off' if not is_collection_synergy_runtime_enabled() else 'runtime_path_not_implemented_in_cs2b',
        'feature_flag': _ENV_VAR,
        'feature_flag_value': bool(is_collection_synergy_runtime_enabled()),
    }


# ---------------------------------------------------------------------------
# Adapter manifest — useful for the safety audit & docs
# ---------------------------------------------------------------------------

ADAPTER_MANIFEST: dict[str, Any] = {
    'adapter_id': 'collection_synergy_preview_resolver_cs2b',
    'task_origin': 'CS2-B',
    'feature_flag_env_var': _ENV_VAR,
    'default_state': 'off',
    'truthy_allowlist': sorted(_TRUTHY_ALLOWLIST),
    'pure_functions': [
        'is_collection_synergy_runtime_enabled',
        'load_collection_synergy_readiness',
        'load_collection_synergy_schema_draft',
        'preview_collection_synergy_categories',
        'preview_collection_milestone_policy',
        'preview_collection_synergy_for_mock_roster',
        'get_disabled_collection_runtime_result',
    ],
    'writes_to_db': False,
    'writes_to_catalogs': False,
    'writes_to_runtime': False,
    'imported_by_battle_engine': False,
    'imported_by_combat_tsx': False,
    'applied_to_combat': False,
    'no_borea_activation': True,
    'forbidden_hero_ids': sorted(_FORBIDDEN_HERO_IDS),
}
