#!/usr/bin/env python3
"""PROJECT_M Track F — rollback script for battle_engine status seam wiring.

The single-point patch in /app/backend/battle_engine.py consists of TWO
sections only:

  1) one import block guarded by try/except that binds the seam to
     ``_project_m_status_seam``;
  2) two single-line calls inside ``simulate_battle()`` that pass team_a /
     team_b through ``_project_m_status_seam``.

This rollback script either:
  - in DRY-RUN mode (default), inspects the file and confirms it knows how
    to undo both sections without modifying anything;
  - in --apply mode, restores from the pre-patch backup if available
    (``/app/backend/battle_engine.py.project_m_pre_patch.bak``); otherwise
    refuses to act.

No destructive action is performed unless ``--apply`` is passed.
"""
import argparse
import hashlib
import shutil
import sys
from pathlib import Path

TARGET = Path('/app/backend/battle_engine.py')
BACKUP = Path('/app/backend/battle_engine.py.project_m_pre_patch.bak')
PATCH_MARKERS = (
    'PROJECT_M Track B — STATUS FIRST SLICE single-point seam import.',
    '_project_m_status_seam',
    'PROJECT_M Track B — pre-fight status seam call (single point).',
)


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='Actually restore battle_engine.py from backup')
    args = ap.parse_args(argv)

    print(f'[ROLLBACK PROJECT_M] target: {TARGET}')
    if not TARGET.exists():
        print('[ABORT] battle_engine.py missing — cannot rollback')
        return 2
    txt = TARGET.read_text(encoding='utf-8', errors='ignore')
    markers_present = sum(1 for m in PATCH_MARKERS if m in txt)
    print(f'[INFO] patch markers detected: {markers_present}/{len(PATCH_MARKERS)}')
    if markers_present == 0:
        print('[INFO] target appears already rolled back — nothing to do')
        return 0

    print(f'[INFO] current md5: {_md5(TARGET)}')
    if BACKUP.exists():
        print(f'[INFO] backup md5: {_md5(BACKUP)} ({BACKUP})')
    else:
        print(f'[WARN] no backup file at {BACKUP} — only manual rollback possible')

    if not args.apply:
        print('[DRY-RUN] no changes made (pass --apply to restore from backup)')
        return 0

    if not BACKUP.exists():
        print('[ABORT] cannot --apply without backup file')
        return 3
    shutil.copy2(BACKUP, TARGET)
    print('[OK] battle_engine.py restored from backup')
    print(f'[INFO] post-restore md5: {_md5(TARGET)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
