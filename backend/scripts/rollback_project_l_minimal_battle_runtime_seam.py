#!/usr/bin/env python3
"""PROJECT_L Track F — rollback script for the minimal inert runtime seam.

This script removes the seam created in Track B. The seam is isolated
(never imported by live runtime), so removal is safe and has no live impact.

The script supports a dry-run inspection mode (default) and an explicit
`--apply` mode that physically deletes the seam file.

Usage:
    python3 rollback_project_l_minimal_battle_runtime_seam.py            # inspection only
    python3 rollback_project_l_minimal_battle_runtime_seam.py --apply    # actually delete
"""
import argparse
import sys
from pathlib import Path

SEAM_FILE = Path('/app/backend/game_logic/status_prefight_runtime_seam.py')
FORBIDDEN_RUNTIME_IMPORTERS = (
    Path('/app/backend/battle_engine.py'),
    Path('/app/backend/battle_core.py'),
    Path('/app/backend/server.py'),
)
FORBIDDEN_IMPORT_PATTERNS = (
    'from .status_prefight_runtime_seam',
    'from backend.game_logic.status_prefight_runtime_seam',
    'from game_logic.status_prefight_runtime_seam',
    'import status_prefight_runtime_seam',
)


def _scan_live_importers() -> list[str]:
    found: list[str] = []
    for f in FORBIDDEN_RUNTIME_IMPORTERS:
        if not f.exists():
            continue
        try:
            txt = f.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        for p in FORBIDDEN_IMPORT_PATTERNS:
            if p in txt:
                found.append(f'{f}: {p}')
    return found


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='Actually delete the seam file')
    args = ap.parse_args(argv)

    print(f'[ROLLBACK PROJECT_L] target: {SEAM_FILE}')
    if not SEAM_FILE.exists():
        print('[INFO] seam already absent — nothing to rollback')
        return 0

    importers = _scan_live_importers()
    if importers:
        print('[ABORT] seam is referenced by live runtime files:')
        for i in importers:
            print(f'  - {i}')
        print('       refuse to rollback automatically; remove import lines first')
        return 2

    if not args.apply:
        print('[DRY-RUN] would delete seam file (pass --apply to execute)')
        print(f'  size: {SEAM_FILE.stat().st_size} bytes')
        return 0

    SEAM_FILE.unlink()
    print('[OK] seam file removed; rollback complete')
    return 0


if __name__ == '__main__':
    sys.exit(main())
