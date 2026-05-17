#!/usr/bin/env python3
"""
RM1.34-B — Pre-patch backup helper for axis patch sources.
Read-only. Copies the source-of-truth design files that PATCH-A and
PATCH-B will mutate, plus the canonical baseline v5, into a timestamped
backup directory under /app/backups/ and writes a sha256 manifest.

NO DB / runtime / catalog mutation occurs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/app')
SOURCES = [
    ROOT / 'data' / 'design' / 'boss_systems' / 'boss_family_element_faction_matrix_v1.json',
    ROOT / 'data' / 'design' / 'boss_systems' / 'boss_family_resistance_table_v1.json',
    ROOT / 'data' / 'design' / 'boss_systems' / 'boss_enrage_phase_policy_table_v1.json',
    ROOT / 'data' / 'design' / 'boss_systems' / 'boss_policy_scenario_fixture_seed_v1.json',
    ROOT / 'data' / 'design' / 'hero_skill_kits' / 'hero_skill_kit_catalog_baseline_rm132c2_v5.json',
    ROOT / 'data' / 'design' / 'shared' / 'canonical_axis_activation_validation_table_v1.json',
    ROOT / 'data' / 'design' / 'shared' / 'canonical_faction_element_axis_resolution_plan_v1.json',
    ROOT / 'data' / 'design' / 'shared' / 'rm134b_patch_readiness_plan_v1.json',
    ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_catalog_faction_element_draft_v1.json',
    ROOT / 'backend' / 'data' / 'canonical_axis_alias_helper.py',
    ROOT / 'backend' / 'data' / 'canonical_axis_read_through_helper.py',
    ROOT / 'backend' / 'scripts' / 'run_hero_skill_kit_validator_suite.py',
]


def sha256_of(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true',
                    help='Only print the manifest plan, do not copy files')
    ap.add_argument('--label', default='axis_patch_rm134b_pre',
                    help='Backup directory label prefix')
    args = ap.parse_args(argv)

    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup_dir = ROOT / 'backups' / f'{args.label}_{ts}'

    print(f'Backup dir: {backup_dir}')
    print(f'Sources: {len(SOURCES)}')

    manifest = {
        'backup_id': f'{args.label}_{ts}',
        'generated_at_utc': ts,
        'task_origin': 'RM1.34-B-PATCH-PRE',
        'design_only': True,
        'runtime_attached': False,
        'db_write': False,
        'no_borea_activation': True,
        'baseline_anchor': 'hero_skill_kit_catalog_baseline_rm132c2_v5',
        'reason': 'Pre-patch backup for RM1.34-B-PATCH-A (darkness->dark) '
                  'and RM1.34-B-PATCH-B (tides deferral). Read-only copy '
                  'of source-of-truth design files plus baseline v5.',
        'rollback_instructions': (
            'To rollback the patch, copy each file under the `files` list '
            'back to its `source` path. Do NOT touch DB, runtime, or '
            'unmentioned files.'
        ),
        'files': [],
    }

    if not args.dry_run:
        backup_dir.mkdir(parents=True, exist_ok=True)

    missing: list[str] = []
    for src in SOURCES:
        if not src.exists():
            missing.append(str(src))
            manifest['files'].append({
                'source': str(src),
                'present_at_backup': False,
                'backup_path': None,
                'sha256': None,
                'size_bytes': 0,
            })
            continue
        rel = src.relative_to(ROOT)
        dest = backup_dir / rel
        if not args.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        sha = sha256_of(src)
        manifest['files'].append({
            'source': str(src),
            'present_at_backup': True,
            'backup_path': str(dest),
            'sha256': sha,
            'size_bytes': src.stat().st_size,
        })

    manifest['missing_count'] = len(missing)
    manifest['missing'] = missing

    if not args.dry_run:
        man_path = backup_dir / 'manifest.json'
        man_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + '\n',
            encoding='utf-8',
        )
        print(f'Manifest written: {man_path}')
    else:
        print('--- dry-run manifest preview ---')
        print(json.dumps(manifest, indent=2, ensure_ascii=False))

    print(f'Backup OK ({len(manifest["files"]) - len(missing)} files, '
          f'{len(missing)} missing)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
