#!/usr/bin/env python3
"""PROJECT_S Track A validator — pure resolver spec lock.

No module creation in Track A: il resolver puo' esistere (creato da Track B),
ma il marker Track A non deve dichiarare module_created_in_track_a=true.
Verifica spec coerente con Track B/C/D.
"""
import json, sys
from pathlib import Path

M = Path('/app/data/design/status_effects/project_s_second_slice_resolver_spec_lock_v1.json')
REQUIRED_IN_SCOPE = {'debuff_offensive', 'debuff_defensive', 'speed_up', 'speed_down'}
REQUIRED_EXCLUDED = {'dot', 'hard_cc', 'shield', 'barrier', 'hot', 'revive', 'borea_marchio'}


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}'); sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_A_SECOND_SLICE_PURE_RESOLVER_SPEC_LOCK_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    if m.get('module_created_in_track_a') is not False:
        fail('module_created_in_track_a must be False (Track A is spec-only)')
    if set(m.get('in_scope_families') or []) != REQUIRED_IN_SCOPE:
        fail(f'in_scope_families mismatch')
    excluded = set(m.get('excluded_families') or [])
    missing = REQUIRED_EXCLUDED - excluded
    if missing:
        fail(f'excluded_families missing entries: {sorted(missing)}')
    mapping = m.get('stat_mapping') or {}
    if mapping.get('debuff_offensive', {}).get('target_stat') != 'atk_pct':
        fail('stat_mapping.debuff_offensive.target_stat must be atk_pct')
    if mapping.get('debuff_defensive', {}).get('target_stat') != 'def_pct':
        fail('stat_mapping.debuff_defensive.target_stat must be def_pct')
    if mapping.get('speed_up', {}).get('target_stat') != 'speed_pct' or mapping.get('speed_down', {}).get('target_stat') != 'speed_pct':
        fail('speed_up/speed_down must target speed_pct')
    caps = m.get('per_status_caps_pct') or {}
    if caps.get('debuff_offensive') != 30.0 or caps.get('debuff_defensive') != 30.0:
        fail('per_status_caps_pct off/def must be 30.0')
    if caps.get('speed_up') != 25.0 or caps.get('speed_down') != 25.0:
        fail('per_status_caps_pct speed must be 25.0')
    mm = m.get('mode_multipliers') or {}
    if mm.get('pvp') > 0.75 or mm.get('boss') > 0.5:
        fail('pvp/boss multipliers out of bounds')
    for k in ('determinism_required', 'side_effect_free_required', 'no_db_imports_required', 'no_http_imports_required', 'no_battle_engine_import_required'):
        if m.get(k) is not True:
            fail(f'{k} must be True')
    if m.get('runtime_activated') is not False:
        fail('runtime_activated must be False')
    print('[PASS] PROJECT_S Track A spec lock READY — 4 families in scope, caps & mode multipliers consistent')
    sys.exit(0)


if __name__ == '__main__': main()
