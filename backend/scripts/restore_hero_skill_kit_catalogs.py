#!/usr/bin/env python3
"""
RM1.32-A-PRE — Hero Skill Kit / Divine Weapon Catalog Restore Helper
─────────────────────────────────────────────────────────────────────────
Restore catalog files from a backup manifest with strict safety gates.

Modes:
  default               : --dry-run is implied (no writes)
  --dry-run             : explicit dry-run
  --commit              : actually restore — REQUIRES env var
                           DIVINE_ALLOW_CATALOG_RESTORE=YES_I_UNDERSTAND

On --commit:
  1. Verify manifest path is under approved backup roots.
  2. Verify every backup file exists and SHA256 matches the manifest.
  3. Create a fresh pre-restore backup of CURRENT catalog state via
     `backup_hero_skill_kit_catalogs.py --reason pre_restore_RM1.32-A-PRE`.
  4. Copy backup files over the source paths.
  5. Run validator suite:
       python3 run_hero_skill_kit_validator_suite.py --include-baseline-diff
  6. If validator suite fails:
       AUTO-ROLLBACK by restoring from the pre-restore backup.
       Exit 1.
  7. Else exit 0.

For RM1.32-A-PRE this script is exercised in --dry-run ONLY. No --commit
will be executed.

NO DB writes. NO runtime changes. NO Borea visibility change.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_MANIFEST_ROOTS = (Path('/app/backups/hero_skill_kits'), Path('/tmp'))
BACKUP_HELPER = Path('/app/backend/scripts/backup_hero_skill_kit_catalogs.py')
SUITE_RUNNER = Path('/app/backend/scripts/run_hero_skill_kit_validator_suite.py')

ENV_VAR = 'DIVINE_ALLOW_CATALOG_RESTORE'
ENV_VALUE = 'YES_I_UNDERSTAND'


def sha256_of(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_manifest(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        print(f'FAIL: cannot read manifest "{path}": {e}')
        return None


def verify_backup_files(manifest: dict) -> tuple[bool, list[str]]:
    issues: list[str] = []
    for entry in manifest.get('files', []):
        bp = Path(entry['backup_path'])
        if not bp.exists():
            issues.append(f'missing backup file: {bp}')
            continue
        cur = sha256_of(bp)
        if cur != entry['sha256']:
            issues.append(f'checksum mismatch on backup file: {bp} '
                          f'(manifest {entry["sha256"][:16]}…, current {cur[:16]}…)')
    return (not issues), issues


def pre_restore_backup(reason: str) -> Path | None:
    cmd = ['python3', str(BACKUP_HELPER), '--reason', reason]
    print(f'  running pre-restore backup: {" ".join(cmd)}')
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except Exception as e:
        print(f'FAIL: cannot run backup helper: {e}')
        return None
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr)
    if proc.returncode != 0:
        return None
    # Extract MANIFEST_PATH from output
    for line in proc.stdout.splitlines():
        if line.startswith('BACKUP_MANIFEST_PATH='):
            return Path(line.split('=', 1)[1].strip())
    return None


def restore_from_manifest(manifest: dict) -> None:
    for entry in manifest.get('files', []):
        src = Path(entry['backup_path'])
        dst = Path(entry['source_path'])
        shutil.copy2(src, dst)


def run_validator_suite() -> bool:
    cmd = ['python3', str(SUITE_RUNNER), '--include-baseline-diff']
    print(f'  running validator suite: {" ".join(cmd)}')
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr)
    return proc.returncode == 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog='restore_hero_skill_kit_catalogs')
    ap.add_argument('--manifest', required=True, help='Path to MANIFEST.json of an existing backup')
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument('--dry-run', action='store_true', help='Explicit dry-run (default mode)')
    grp.add_argument('--commit', action='store_true',
                     help=f'Actually restore. REQUIRES env var {ENV_VAR}={ENV_VALUE}')
    args = ap.parse_args(argv)

    manifest_path = Path(args.manifest).resolve()
    if not any(str(manifest_path).startswith(str(r.resolve())) for r in ALLOWED_MANIFEST_ROOTS):
        print(f'REJECTED: manifest path "{manifest_path}" is outside allowed roots: '
              f'{[str(r) for r in ALLOWED_MANIFEST_ROOTS]}')
        return 2
    if not manifest_path.exists():
        print(f'FAIL: manifest not found: {manifest_path}')
        return 1

    manifest = load_manifest(manifest_path)
    if manifest is None:
        return 1

    print(f'[RM1.32-A-PRE] Restore helper')
    print(f'  manifest        : {manifest_path}')
    print(f'  backup_id       : {manifest.get("backup_id")}')
    print(f'  manifest task   : {manifest.get("task_origin")}')
    print(f'  manifest reason : {manifest.get("reason")}')
    print(f'  files to restore: {len(manifest.get("files") or [])}')

    ok, issues = verify_backup_files(manifest)
    if not ok:
        print('FAIL: backup integrity verification failed:')
        for i in issues:
            print(f'  - {i}')
        return 1
    print('  backup integrity: OK (all checksums match)')

    if not args.commit:
        print('  mode            : DRY-RUN (no files restored)')
        print('OK: dry-run complete. To commit a real restore you must:')
        print(f'  1. export {ENV_VAR}={ENV_VALUE}')
        print('  2. re-run with --commit')
        return 0

    # COMMIT path
    print('  mode            : COMMIT')
    env_val = os.environ.get(ENV_VAR)
    if env_val != ENV_VALUE:
        print(f'REJECTED: --commit requires env var {ENV_VAR}={ENV_VALUE} (got {env_val!r}).')
        return 3

    # Pre-restore backup
    pre_manifest = pre_restore_backup('pre_restore_RM1.32-A-PRE')
    if pre_manifest is None or not pre_manifest.exists():
        print('FAIL: pre-restore backup could not be created.')
        return 1
    print(f'  pre-restore backup manifest: {pre_manifest}')

    # Apply restore
    try:
        restore_from_manifest(manifest)
    except Exception as e:
        print(f'FAIL during restore: {e}')
        return 1

    # Run validator suite
    if run_validator_suite():
        print('OK: restore committed and validator suite PASS.')
        return 0

    # AUTO-ROLLBACK
    print('VALIDATOR SUITE FAILED — auto-rollback engaged.')
    try:
        pre = load_manifest(pre_manifest)
        if pre is None:
            print('FAIL: cannot load pre-restore manifest for rollback.')
            return 1
        restore_from_manifest(pre)
        print('OK: rollback complete (catalogs restored to pre-restore state).')
    except Exception as e:
        print(f'FATAL: rollback failed: {e}')
        return 1
    return 1


if __name__ == '__main__':
    sys.exit(main())
