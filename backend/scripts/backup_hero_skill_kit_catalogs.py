#!/usr/bin/env python3
"""
RM1.32-A-PRE — Hero Skill Kit / Divine Weapon Catalog Backup Helper
─────────────────────────────────────────────────────────────────────────
Create timestamped backups + manifest of critical catalog files.
READ-ONLY against source catalogs (source files are never modified).

Usage:
  python3 backup_hero_skill_kit_catalogs.py [--dry-run] [--reason TEXT]
                                            [--out-dir PATH]

Output layout (default):
  /app/backups/hero_skill_kits/<backup_id>/
    hero_skill_kits_5star_full_v1.json
    hero_skill_kits_6star_borea_v1.json
    divine_weapons_catalog_v1.json
    hero_skill_kit_schema_v1.json
    hero_skill_kit_catalog_baseline_rm132pre_v1.json
    MANIFEST.json
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCES = [
    Path('/app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json'),
    Path('/app/data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json'),
    Path('/app/data/design/divine_weapons/divine_weapons_catalog_v1.json'),
    Path('/app/data/design/hero_skill_kits/hero_skill_kit_schema_v1.json'),
    Path('/app/data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132pre_v1.json'),
]
DEFAULT_OUT = Path('/app/backups/hero_skill_kits')
SAFE_OUT_ROOTS = (Path('/app/backups/hero_skill_kits'), Path('/tmp'))


def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog='backup_hero_skill_kit_catalogs')
    ap.add_argument('--dry-run', action='store_true',
                    help='Plan only; do not write backup files')
    ap.add_argument('--reason', default='unspecified',
                    help='Reason for the backup (free text)')
    ap.add_argument('--out-dir', default=str(DEFAULT_OUT),
                    help=f'Output root (must be under one of {[str(s) for s in SAFE_OUT_ROOTS]})')
    args = ap.parse_args(argv)

    out_root = Path(args.out_dir).resolve()
    if not any(str(out_root).startswith(str(s.resolve())) for s in SAFE_OUT_ROOTS):
        print(f'REJECTED: --out-dir "{out_root}" is outside allowed roots: {[str(s) for s in SAFE_OUT_ROOTS]}')
        return 2

    # Verify sources
    missing = [str(s) for s in SOURCES if not s.exists()]
    if missing:
        print('FAIL: missing source(s):')
        for m in missing:
            print(f'  - {m}')
        return 1

    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup_id = f'backup_{ts}'
    backup_dir = out_root / backup_id

    print(f'[RM1.32-A-PRE] Backup helper {"(DRY-RUN)" if args.dry_run else ""}')
    print(f'  backup_id : {backup_id}')
    print(f'  out_dir   : {backup_dir}')
    print(f'  reason    : {args.reason}')
    print(f'  files     : {len(SOURCES)}')

    entries = []
    if not args.dry_run:
        backup_dir.mkdir(parents=True, exist_ok=False)
    for src in SOURCES:
        sha = sha256_of(src)
        size = src.stat().st_size
        target = backup_dir / src.name
        if not args.dry_run:
            shutil.copy2(src, target)
            # Verify post-copy checksum matches
            post_sha = sha256_of(target)
            if post_sha != sha:
                print(f'FAIL: post-copy checksum mismatch for {target}')
                return 1
        entries.append({
            'source_path': str(src),
            'backup_path': str(target),
            'sha256': sha,
            'size_bytes': size,
        })
        print(f'    ✓ {src.name} ({size:>9} bytes, sha256={sha[:16]}…)')

    manifest = {
        'manifest_id': 'hero_skill_kit_backup_manifest',
        'backup_id': backup_id,
        'task_origin': 'RM1.32-A-PRE',
        'created_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'reason': args.reason,
        'dry_run': args.dry_run,
        'out_dir': str(backup_dir),
        'files': entries,
        'safety_flags': {
            'catalog_only': True,
            'no_db_write': True,
            'no_runtime': True,
            'borea_visibility_unchanged': True,
        },
    }
    manifest_path = backup_dir / 'MANIFEST.json'
    if not args.dry_run:
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(f'  manifest  : {manifest_path}')
    else:
        print('  manifest  : <DRY-RUN, not written>')

    print(f'OK: backup {"planned" if args.dry_run else "created"} ({len(SOURCES)} files).')
    if not args.dry_run:
        # Print machine-grepable line
        print(f'BACKUP_MANIFEST_PATH={manifest_path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
