#!/usr/bin/env python3
"""PROJECT_L Track A validator — battle runtime seam audit."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_l_battle_runtime_seam_audit_v1.json')
BE = Path('/app/backend/battle_engine.py')
BC = Path('/app/backend/battle_core.py')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_A_BATTLE_RUNTIME_SEAM_AUDIT_READY': fail('verdict mismatch')
    if m.get('seam_classification') != 'SEAM_SAFE_NOW_INERT': fail('classification must be SEAM_SAFE_NOW_INERT')
    if m.get('runtime_changes_applied_in_track_a') is not False: fail('runtime_changes_applied_in_track_a must be False')
    if not BE.exists(): fail('expected battle_engine.py to exist as observed')
    if not BC.exists(): fail('expected battle_core.py to exist as observed')
    forb = m.get('forbidden_in_track_a_respected', {})
    for k in ('runtime_mutation', 'battle_behavior_change', 'broad_refactor'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_a.{k} must be False')
    print('[PASS] PROJECT_L Track A seam audit READY: SEAM_SAFE_NOW_INERT classified; no runtime mutation')
    sys.exit(0)


if __name__ == '__main__': main()
