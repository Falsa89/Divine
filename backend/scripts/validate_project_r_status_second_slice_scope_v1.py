#!/usr/bin/env python3
"""PROJECT_R Track A validator — status second slice scope + boundary.

Verifica scope esatto (4 famiglie) e esclusioni hard (DoT, CC, shield, HoT, revive,
immunity/cleanse runtime, Borea Marchio live). Design-only: nessun runtime touched.
"""
import json, sys
from pathlib import Path

M = Path('/app/data/design/status_effects/project_r_status_second_slice_scope_v1.json')
REQUIRED_IN_SCOPE = {'debuff_offensive', 'debuff_defensive', 'speed_up', 'speed_down'}
REQUIRED_EXCLUDED = {'dot', 'poison', 'burn', 'bleed', 'freeze', 'stun', 'sleep', 'hard_cc', 'shield', 'barrier', 'hot', 'revive', 'immunity_cleanse_runtime', 'borea_marchio_live_logic'}


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_A_STATUS_SECOND_SLICE_SCOPE_AND_BOUNDARY_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    if m.get('design_only') is not True or m.get('runtime_activated') is not False:
        fail('must be design_only and not runtime_activated')
    in_scope = set(m.get('second_slice_in_scope') or [])
    if in_scope != REQUIRED_IN_SCOPE:
        fail(f'second_slice_in_scope mismatch: {in_scope} != {REQUIRED_IN_SCOPE}')
    excluded = set(m.get('second_slice_excluded') or [])
    missing = REQUIRED_EXCLUDED - excluded
    if missing:
        fail(f'second_slice_excluded missing entries: {sorted(missing)}')
    if m.get('battle_engine_touched') is not False or m.get('battle_core_touched') is not False or m.get('frontend_touched') is not False:
        fail('design pack must not touch battle_engine/battle_core/frontend')
    if m.get('db_writes') is not False:
        fail('db_writes must be False')
    print('[PASS] PROJECT_R Track A scope READY — 4 families in scope, hard exclusions in place, no runtime touch')
    sys.exit(0)


if __name__ == '__main__':
    main()
