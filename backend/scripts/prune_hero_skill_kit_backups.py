#!/usr/bin/env python3
"""
RM1.32-A-PRE-C — Hero Skill Kit Backup Retention / Prune Helper
─────────────────────────────────────────────────────────────────────────
Prune older backup directories under /app/backups/hero_skill_kits/
keeping only the N most-recent ones.

Default mode is DRY-RUN. Real deletion requires:
  DIVINE_ALLOW_BACKUP_PRUNE=YES_I_UNDERSTAND  (env var)
  --commit                                     (CLI flag)

Safety rules:
  - Backup root must be under /app/backups/hero_skill_kits/ or /tmp.
  - Never touches current active catalog files.
  - Never touches files outside the backup root.
  - Only prunes directories that look like a valid backup:
      directory name starts with "backup_"
      MANIFEST.json present in the directory
      MANIFEST.json parseable JSON
  - Sort by manifest.created_at_utc when available, fall back to
    directory name (timestamp-prefixed) and finally mtime.
  - Refuse to prune if --keep < 1.
  - Refuse to commit-delete if it would delete the newest backup.

Usage:
  python3 prune_hero_skill_kit_backups.py [--keep 10] [--dry-run|--commit]
                                          [--backup-root PATH]
"""
from __future__ import annotations
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

DEFAULT_ROOT = Path('/app/backups/hero_skill_kits')
ALLOWED_ROOTS = (Path('/app/backups/hero_skill_kits'), Path('/tmp'))
ENV_VAR = 'DIVINE_ALLOW_BACKUP_PRUNE'
ENV_VALUE = 'YES_I_UNDERSTAND'


def parse_backup_dir(d: Path) -> dict | None:
    """Return a dict describing this backup dir, or None if invalid."""
    if not d.is_dir():
        return None
    if not d.name.startswith('backup_'):
        return None
    manifest_path = d / 'MANIFEST.json'
    if not manifest_path.exists():
        return None
    try:
        m = json.loads(manifest_path.read_text(encoding='utf-8'))
    except Exception:
        return None
    sort_key = m.get('created_at_utc') or d.name
    return {
        'path': d,
        'manifest_path': manifest_path,
        'created_at_utc': m.get('created_at_utc'),
        'backup_id': m.get('backup_id', d.name),
        'reason': m.get('reason'),
        'files_count': len(m.get('files') or []),
        'sort_key': sort_key,
        'mtime': d.stat().st_mtime,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog='prune_hero_skill_kit_backups')
    ap.add_argument('--keep', type=int, default=10, help='Number of most-recent backups to keep (default: 10)')
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument('--dry-run', action='store_true', help='Explicit dry-run (default mode)')
    grp.add_argument('--commit', action='store_true',
                     help=f'Really delete older backups. REQUIRES env {ENV_VAR}={ENV_VALUE}')
    ap.add_argument('--backup-root', default=str(DEFAULT_ROOT),
                    help=f'Backup root (must be under {[str(r) for r in ALLOWED_ROOTS]})')
    args = ap.parse_args(argv)

    if args.keep < 1:
        print('REJECTED: --keep must be >= 1.')
        return 2

    root = Path(args.backup_root).resolve()
    if not any(str(root).startswith(str(r.resolve())) for r in ALLOWED_ROOTS):
        print(f'REJECTED: --backup-root "{root}" outside allowed roots: {[str(r) for r in ALLOWED_ROOTS]}')
        return 2
    if not root.exists():
        print(f'INFO: backup root "{root}" does not exist; nothing to prune.')
        return 0
    if not root.is_dir():
        print(f'REJECTED: "{root}" is not a directory.')
        return 2

    candidates = []
    skipped = []
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        info = parse_backup_dir(d)
        if info is None:
            skipped.append(str(d))
            continue
        candidates.append(info)

    # Sort by sort_key DESC (newest first)
    candidates.sort(key=lambda x: (x['sort_key'] or '', x['mtime']), reverse=True)

    keep = candidates[:args.keep]
    prune = candidates[args.keep:]

    print(f'[RM1.32-A-PRE-C] prune_hero_skill_kit_backups')
    print(f'  backup_root : {root}')
    print(f'  keep N      : {args.keep}')
    print(f'  total dirs  : {len(candidates)}')
    print(f'  would keep  : {len(keep)}')
    print(f'  would prune : {len(prune)}')
    if skipped:
        print(f'  skipped (no MANIFEST or invalid): {len(skipped)}')
        for s in skipped:
            print(f'    ! {s}')

    print('--- KEEP ---')
    for i, info in enumerate(keep, 1):
        print(f'  {i:2d}. {info["backup_id"]:35s} files={info["files_count"]:>2} reason={info.get("reason")!s}')
    print('--- PRUNE candidates ---')
    if not prune:
        print('  (none)')

    for i, info in enumerate(prune, 1):
        print(f'  {i:2d}. {info["backup_id"]:35s} files={info["files_count"]:>2} reason={info.get("reason")!s}')

    if not args.commit:
        print('mode        : DRY-RUN (no deletion)')
        if prune:
            print(f'To commit deletion: export {ENV_VAR}={ENV_VALUE} && re-run with --commit')
        return 0

    # COMMIT path
    print('mode        : COMMIT')
    env_val = os.environ.get(ENV_VAR)
    if env_val != ENV_VALUE:
        print(f'REJECTED: --commit requires env {ENV_VAR}={ENV_VALUE} (got {env_val!r}).')
        return 3
    if not prune:
        print('OK: nothing to delete.')
        return 0
    # Extra safety: never delete the newest backup
    newest_id = keep[0]['backup_id'] if keep else None
    deleted = 0
    for info in prune:
        if info['backup_id'] == newest_id:
            print(f'REFUSING to delete newest backup: {info["backup_id"]}')
            continue
        try:
            shutil.rmtree(info['path'])
            print(f'  DELETED: {info["path"]}')
            deleted += 1
        except Exception as e:
            print(f'  FAIL deleting {info["path"]}: {e}')
            return 1
    print(f'OK: pruned {deleted} backup directories. Kept {len(keep)}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
