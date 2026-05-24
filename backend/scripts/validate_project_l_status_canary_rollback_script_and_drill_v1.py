#!/usr/bin/env python3
"""PROJECT_L Track F validator — status canary rollback script + drill."""
import json, subprocess, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_l_status_canary_rollback_script_and_drill_v1.json')
ROLLBACK = Path('/app/backend/scripts/rollback_project_l_minimal_battle_runtime_seam.py')
SEAM = Path('/app/backend/game_logic/status_prefight_runtime_seam.py')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_F_STATUS_CANARY_ROLLBACK_SCRIPT_AND_DRILL_READY': fail('verdict mismatch')
    if not ROLLBACK.exists(): fail('rollback script missing')
    if m.get('destructive_rollback_executed') is not False: fail('destructive_rollback_executed must be False')
    # Execute dry-run; must succeed and must NOT delete the seam.
    if not SEAM.exists(): fail('seam must exist BEFORE drill (this also confirms drill is non-destructive)')
    pre_size = SEAM.stat().st_size
    proc = subprocess.run(['python3', str(ROLLBACK)], capture_output=True, text=True, timeout=30)
    if proc.returncode != 0: fail(f'dry-run drill rc={proc.returncode}: {proc.stderr or proc.stdout}')
    if 'DRY-RUN' not in proc.stdout: fail('drill must print DRY-RUN marker')
    if not SEAM.exists(): fail('drill must NOT delete the seam in dry-run mode')
    if SEAM.stat().st_size != pre_size: fail('seam file modified during dry-run drill')
    print('[PASS] PROJECT_L Track F rollback script + drill READY: dry-run OK; seam preserved; no destructive action')
    sys.exit(0)


if __name__ == '__main__': main()
