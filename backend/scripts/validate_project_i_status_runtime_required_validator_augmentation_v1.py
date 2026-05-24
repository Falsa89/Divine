#!/usr/bin/env python3
"""PROJECT_I Track C validator — status runtime REQUIRED validator augmentation prep."""
import json, sys
from pathlib import Path

MARKER = Path('/app/data/design/status_effects/project_i_status_runtime_required_validator_augmentation_v1.json')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_C_STATUS_RUNTIME_REQUIRED_VALIDATOR_AUGMENTATION_READY': fail('verdict mismatch')
    if m.get('runtime_changes_applied') is not False: fail('runtime_changes_applied must be False')
    if m.get('runtime_active') is not False: fail('runtime_active must be False')
    planned = m.get('planned_required_validators_for_first_slice_activation', [])
    if len(planned) < 5: fail('at least 5 planned REQUIRED validators must be listed')
    for p in planned:
        for k in ('validator_name', 'asserts', 'required_when'):
            if k not in p: fail(f'planned validator missing field: {k}')
        if p.get('required_when') != 'STATUS_RUNTIME_BUFF_SLICE_ENABLED=true':
            fail(f'planned validator required_when mismatch: {p.get("required_when")}')
    if m.get('validators_actually_added_to_required_in_pack_i') != 0:
        fail('validators_actually_added_to_required_in_pack_i must be 0 (zero-coupling between prep and activation)')
    if m.get('required_diff_guard_preserved') is not True: fail('required_diff_guard_preserved must be True')
    forb = m.get('forbidden_in_track_c_respected', {})
    for k in ('battle_mutation', 'runtime_status_activation', 'battle_engine_change', 'battle_core_change', 'combat_tsx_change', 'required_weakening'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_c.{k} must be False')
    print('[PASS] PROJECT_I Track C status runtime REQUIRED validator augmentation READY: 5+ planned validators; zero added in pack I; required diff guard preserved')
    sys.exit(0)

if __name__ == '__main__': main()
