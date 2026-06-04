#!/usr/bin/env python3
"""validate_menu_public_exposure_dryrun_blocked_v1

Validator OPTIONAL read-only.
Verifica:
- dry-run result presente con applied=false
- apply_or_blocked result con verdict BLOCKED_NOT_APPLIED_SAFE
- failed_gate=manual_approval_missing
- production_navigation_changed=false, db_writes=0
- marker dryrun_blocked coerente
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PREFIX = 'PROJECT-MENU-PUBLIC-EXPOSURE-DRYRUN-BLOCKED'
TAG = 'PUBLIC_SYNC_TAG_v73_MEGA_RELEASE_ACCELERATION_22_MENU_EXPOSURE_CLOSED_ALPHA'

FILES = [
    'data/design/navigation/menu_public_exposure_dry_run_result_v1.json',
    'data/design/navigation/menu_public_exposure_apply_or_blocked_result_v1.json',
    'data/design/navigation/menu_public_exposure_dryrun_blocked_marker_v1.json',
]


def fail(msg: str) -> None:
    print(f'{PREFIX}: FAIL {msg}')
    sys.exit(1)


def main() -> None:
    for rel in FILES:
        p = ROOT / rel
        if not p.exists():
            fail(f'missing {rel}')
        try:
            json.loads(p.read_text())
        except Exception as e:
            fail(f'invalid JSON {rel}: {e}')

    dry = json.loads((ROOT / FILES[0]).read_text())
    blk = json.loads((ROOT / FILES[1]).read_text())
    mrk = json.loads((ROOT / FILES[2]).read_text())

    if dry.get('dry_run') is not True:
        fail('dry_run must be true')
    if dry.get('applied') is not False:
        fail('dry_run.applied must be false')
    if dry.get('production_navigation_changed') is not False:
        fail('dry_run.production_navigation_changed must be false')
    if dry.get('public_menu_exposure_enabled') is not False:
        fail('dry_run.public_menu_exposure_enabled must be false')
    if dry.get('db_writes') != 0:
        fail('dry_run.db_writes must be 0')
    if dry.get('summary', {}).get('only_failed_gate') != 'manual_approval_received':
        fail('dry_run.only_failed_gate must be manual_approval_received')

    if blk.get('applied') is not False:
        fail('blocked.applied must be false')
    if blk.get('verdict') != 'BLOCKED_NOT_APPLIED_SAFE':
        fail('blocked.verdict must be BLOCKED_NOT_APPLIED_SAFE')
    if blk.get('failed_gate') != 'manual_approval_missing':
        fail('blocked.failed_gate must be manual_approval_missing')
    if blk.get('production_navigation_changed') is not False:
        fail('blocked.production_navigation_changed must be false')
    if blk.get('public_menu_exposure_enabled') is not False:
        fail('blocked.public_menu_exposure_enabled must be false')
    if blk.get('file_changes_to_public_navigation') != 0:
        fail('blocked.file_changes_to_public_navigation must be 0')
    if blk.get('db_writes') != 0:
        fail('blocked.db_writes must be 0')

    if mrk.get('verdict') != 'BLOCKED_NOT_APPLIED_SAFE':
        fail('marker.verdict mismatch')
    if mrk.get('public_sync_tag') != TAG:
        fail('marker.public_sync_tag mismatch')
    if mrk.get('db_writes') != 0:
        fail('marker.db_writes must be 0')

    print(f'{PREFIX}: PASS')


if __name__ == '__main__':
    main()
