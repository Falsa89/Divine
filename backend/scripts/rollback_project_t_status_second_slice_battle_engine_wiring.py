#!/usr/bin/env python3
"""PROJECT_T Track B/F — rollback for the second-slice single-point wiring in battle_engine.py.

GATED. Two-phase rollback:
  1) Removes the seam module file `status_second_slice_runtime_seam.py`.
  2) Restores `battle_engine.py` from the pre-patch backup created at wire time.

Usage:
    python3 rollback_project_t_status_second_slice_battle_engine_wiring.py             # dry-run report
    python3 rollback_project_t_status_second_slice_battle_engine_wiring.py --execute   # GATED on env marker

Gate env marker required for --execute:
    PROJECT_T_ROLLBACK_SECOND_SLICE_WIRING_OK=true
"""
from __future__ import annotations

import argparse, os, shutil, sys
from pathlib import Path

SEAM_MODULE = Path('/app/backend/game_logic/status_second_slice_runtime_seam.py')
BATTLE_ENGINE = Path('/app/backend/battle_engine.py')
BACKUP = Path('/app/backend/battle_engine.py.project_t_pre_wire_backup')
GATE_ENV = 'PROJECT_T_ROLLBACK_SECOND_SLICE_WIRING_OK'

FORBIDDEN_TO_DELETE = (
    Path('/app/backend/game_logic/status_first_slice_resolver_pure.py'),
    Path('/app/backend/game_logic/status_prefight_runtime_seam.py'),
    Path('/app/backend/game_logic/status_second_slice_resolver_pure.py'),
    Path('/app/backend/battle_core.py'),
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--execute', action='store_true', help='actually rollback; GATED on env marker')
    args = ap.parse_args()

    seam_present = SEAM_MODULE.exists()
    backup_present = BACKUP.exists()
    print(f'[INFO] seam module present : {seam_present}  ({SEAM_MODULE})')
    print(f'[INFO] battle_engine backup: {backup_present} ({BACKUP})')
    if backup_present:
        print(f'[INFO] would restore battle_engine.py from backup')
    if seam_present:
        print(f'[INFO] would delete seam module')

    for fp in FORBIDDEN_TO_DELETE:
        if not fp.exists():
            print(f'[ABORT] forbidden file missing pre-rollback (refusing to proceed): {fp}')
            return 4

    if not args.execute:
        print('[DRY-RUN] no changes applied; pass --execute (with env gate) to rollback')
        return 0

    if os.environ.get(GATE_ENV, '').strip().lower() != 'true':
        print(f'[ABORT] --execute requires {GATE_ENV}=true (not set); refusing rollback')
        return 3

    rc = 0
    if backup_present:
        try:
            shutil.copyfile(str(BACKUP), str(BATTLE_ENGINE))
            print(f'[OK] restored {BATTLE_ENGINE} from backup')
        except Exception as e:
            print(f'[ERR] battle_engine restore failed: {e}'); rc = 1
    else:
        print('[WARN] no backup found; battle_engine.py not modified by rollback')
    if seam_present:
        try:
            SEAM_MODULE.unlink()
            print(f'[OK] removed seam module {SEAM_MODULE}')
        except Exception as e:
            print(f'[ERR] seam module removal failed: {e}'); rc = 1

    # Final verification: forbidden files still intact
    for fp in FORBIDDEN_TO_DELETE:
        if not fp.exists():
            print(f'[CRITICAL] forbidden file disappeared post-rollback: {fp}')
            return 5
    print('[DONE] rollback complete')
    return rc


if __name__ == '__main__':
    sys.exit(main())
