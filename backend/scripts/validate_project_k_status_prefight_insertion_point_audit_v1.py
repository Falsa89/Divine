#!/usr/bin/env python3
"""PROJECT_K Track A validator — pre-fight insertion point audit."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_k_status_prefight_insertion_point_audit_v1.json')
ABSENT_PATHS = (Path('/app/backend/game_logic/battle_engine.py'), Path('/app/backend/game_logic/battle_core.py'), Path('/app/frontend/components/combat.tsx'))
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_A_STATUS_PREFIGHT_INSERTION_POINT_AUDIT_BLOCKER_NO_BATTLE_RUNTIME_LAYER': fail('verdict mismatch')
    if m.get('safe_to_wire') is not False: fail('safe_to_wire must be False')
    if m.get('battle_runtime_layer_present') is not False: fail('battle_runtime_layer_present must be False')
    # Verify the files really are absent (honest gating)
    for p in ABSENT_PATHS:
        if p.exists(): fail(f'unexpected presence of {p} — audit must be re-run')
    if m.get('runtime_changes_applied_in_track_a') is not False: fail('runtime_changes_applied must be False')
    print('[PASS] PROJECT_K Track A audit: NO battle runtime layer; wiring deferred safely')
    sys.exit(0)
if __name__ == '__main__': main()
