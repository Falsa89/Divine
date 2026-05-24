#!/usr/bin/env python3
"""PROJECT_H Track C validator — final status runtime gate + first slice plan."""
import json, sys
from pathlib import Path

MARKER = Path('/app/data/design/status_effects/project_h_final_status_runtime_gate_and_first_slice_v1.json')
FORBIDDEN_IMPORT_TARGETS = (
    Path('/app/backend/game_logic/battle_engine.py'),
    Path('/app/backend/game_logic/battle_core.py'),
    Path('/app/frontend/components/combat.tsx'),
)
NEEDLE = 'status_effect_runtime_adapter_stub'


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_C_FINAL_STATUS_RUNTIME_GATE_READY': fail('verdict mismatch')
    if m.get('runtime_changes_applied') is not False: fail('runtime_changes_applied must be False')
    if m.get('runtime_active') is not False: fail('runtime_active must be False')
    slice_def = m.get('first_safe_runtime_slice', {})
    if not slice_def: fail('first_safe_runtime_slice missing')
    if slice_def.get('live_battle_mutation') is not False: fail('first_safe_runtime_slice.live_battle_mutation must be False')
    if slice_def.get('tick_loop_touched') is not False: fail('first_safe_runtime_slice.tick_loop_touched must be False')
    if set(slice_def.get('categories', [])) != {'buff_offensive', 'buff_defensive'}:
        fail('first slice categories must be {buff_offensive, buff_defensive}')
    if not slice_def.get('flag_required_for_runtime'): fail('first slice flag_required_for_runtime missing')
    if not isinstance(m.get('blockers_for_actual_battle_integration', []), list) or len(m['blockers_for_actual_battle_integration']) < 3:
        fail('blockers_for_actual_battle_integration must list at least 3 blockers')
    tests = m.get('test_matrix', [])
    if len(tests) < 6: fail('test_matrix must have at least 6 UTs')
    forb = m.get('forbidden_in_track_c_respected', {})
    for k in ('battle_mutation', 'runtime_status_activation', 'battle_engine_change', 'battle_core_change', 'combat_tsx_change'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_c.{k} must be False')
    # Adapter NOT imported by battle/runtime
    for p in FORBIDDEN_IMPORT_TARGETS:
        if p.exists() and NEEDLE in p.read_text():
            fail(f'adapter must NOT be imported by {p}')
    print('[PASS] PROJECT_H Track C final status runtime gate READY: first slice (buff_off+def) planned read-only; no live mutation; 6 UTs defined')
    sys.exit(0)

if __name__ == '__main__': main()
