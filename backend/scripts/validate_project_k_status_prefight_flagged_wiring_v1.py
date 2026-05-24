#!/usr/bin/env python3
"""PROJECT_K Track B validator — wiring NOT applied (Track A blocker)."""
import importlib.util, json, os, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_k_status_prefight_flagged_wiring_v1.json')
R = Path('/app/backend/game_logic/status_first_slice_resolver_pure.py')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_B_STATUS_PREFIGHT_FLAGGED_WIRING_NOT_APPLIED_AWAITING_BATTLE_RUNTIME_LAYER': fail('verdict mismatch')
    if m.get('wiring_applied') is not False: fail('wiring_applied must be False')
    if m.get('local_backend_behavior_preserved') is not True: fail('local_backend_behavior_preserved must be True')
    if m.get('runtime_changes_applied') is not False: fail('runtime_changes_applied must be False')
    # Honest invariant: flag default still OFF; resolver inactive
    if os.environ.get('STATUS_RUNTIME_BUFF_SLICE_ENABLED', '').strip().lower() == 'true':
        fail('flag must be OFF in local backend env')
    spec = importlib.util.spec_from_file_location('_r', R); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    if mod.is_runtime_active(): fail('resolver.is_runtime_active() must be False')
    print('[PASS] PROJECT_K Track B wiring NOT applied (honest blocker recorded); flag OFF; resolver inactive')
    sys.exit(0)
if __name__ == '__main__': main()
