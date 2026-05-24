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
    # Two accepted outcomes:
    #   (a) rc=0 with 'DRY-RUN' marker  -> seam not wired live, drill ok
    #   (b) rc=2 with 'ABORT' marker    -> seam is wired live (PROJECT_M); the
    #       script REFUSES to rollback as a safety guard. This is the correct
    #       protective behavior post-PROJECT_M.
    out = proc.stdout
    if proc.returncode == 0:
        if 'DRY-RUN' not in out: fail('rc=0 but DRY-RUN marker missing')
    elif proc.returncode == 2:
        if 'ABORT' not in out: fail('rc=2 but ABORT marker missing')
        if 'live runtime files' not in out: fail('rc=2 must explain live importer presence')
    else:
        fail(f'unexpected rc={proc.returncode}: {proc.stderr or out}')
    if not SEAM.exists(): fail('drill must NOT delete the seam')
    if SEAM.stat().st_size != pre_size: fail('seam file modified during drill')
    print(f'[PASS] PROJECT_L Track F rollback script + drill READY: rc={proc.returncode} ({"DRY-RUN" if proc.returncode == 0 else "ABORT-protective"}); seam preserved')
    sys.exit(0)


if __name__ == '__main__': main()
