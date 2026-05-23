#!/usr/bin/env python3
"""
SLC-F MINOR WRITE SURFACES AUDIT (READ-ONLY)

Audit script that scans backend/routes/*.py for write surfaces and
verifies the classification matches the canonical audit JSON.
This script PERFORMS NO RUNTIME PATCHES, NO DB WRITES, NO MIGRATIONS.

It also doubles as a validator: it confirms that previously-patched
files still contain the helper import and the audit JSON is consistent
with on-disk state.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
ROUTES_DIR = ROOT / 'backend' / 'routes'
AUDIT_JSON = ROOT / 'data/design/system_safety/slc_f_minor_write_surfaces_audit_v1.json'
OUT = ROOT / 'data/design/server_lifecycle/_slc_f_minor_write_surfaces_audit_v1_result.json'

WRITE_PAT = re.compile(r'(db\.\w+)\.(insert_one|insert_many|update_one|update_many|replace_one|find_one_and_update|find_one_and_replace)\s*\(')
UPSERT_PAT = re.compile(r'upsert\s*=\s*True')
HELPER_IMPORT = 'from utils.server_scope import ensure_server_scope'

EXPECTED_HELPER_FILES = {
    'hero_progression.py', 'items.py', 'forge.py', 'achievements.py',
    'level_sharing.py', 'social.py', 'soul_forge.py', 'artifacts.py',
    'guild.py', 'raids.py',
}


def main() -> int:
    errs = []

    if not AUDIT_JSON.exists():
        errs.append('audit_json_missing')
        out = {'verdict': 'FAIL', 'errors': errs}
        OUT.write_text(json.dumps(out, indent=2))
        return 1

    audit = json.loads(AUDIT_JSON.read_text())
    if audit.get('scope') != 'AUDIT_ONLY':
        errs.append('audit_scope_must_be_AUDIT_ONLY')
    if audit.get('runtime_files_modified') is not False:
        errs.append('audit_must_assert_no_runtime_modifications')
    if audit.get('db_writes_performed') is not False:
        errs.append('audit_must_assert_no_db_writes')

    # Verify expected helper files still contain the helper import
    for fname in sorted(EXPECTED_HELPER_FILES):
        text = (ROUTES_DIR / fname).read_text(errors='ignore')
        if HELPER_IMPORT not in text:
            errs.append(f'helper_import_missing_in:{fname}')

    # Re-scan all route files and confirm we still detect ~201 write surfaces
    total = 0
    files_with_writes = 0
    for f in sorted(ROUTES_DIR.glob('*.py')):
        if f.name == '__init__.py':
            continue
        n = len(WRITE_PAT.findall(f.read_text()))
        if n > 0:
            files_with_writes += 1
            total += n
    expected_total = audit.get('total_write_surfaces_detected')
    if expected_total is not None and abs(total - expected_total) > 5:
        errs.append(f'write_surface_count_drift:{total}_vs_audit_{expected_total}')

    # Confirm classification table covers all helper-imported files as ALREADY_PATCHED_SAFE
    rows = audit.get('classification_table') or []
    patched_in_audit = {Path(r.get('file', '')).name for r in rows if r.get('classification') == 'ALREADY_PATCHED_SAFE'}
    missing = EXPECTED_HELPER_FILES - patched_in_audit
    if missing:
        errs.append(f'expected_helper_files_not_marked_already_patched:{sorted(missing)}')

    # Confirm at least 1 SAFE_MICRO_BATCH_CANDIDATE present (the whole point of audit)
    candidates = [r for r in rows if r.get('classification') == 'SAFE_MICRO_BATCH_CANDIDATE']
    if not candidates:
        errs.append('no_safe_micro_batch_candidate_identified')

    # Confirm recommended_next_micro_batches is non-empty and has explicit markers
    next_batches = audit.get('recommended_next_micro_batches') or []
    if not next_batches:
        errs.append('recommended_next_micro_batches_empty')
    for nb in next_batches:
        if not nb.get('requires_markers'):
            errs.append(f'next_batch_missing_markers:{nb.get("name")}')

    out = {
        'task_origin': 'SLC-F-MINOR-WRITE-SURFACES-AUDIT-V1',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'write_surfaces_rescanned_total': total,
        'files_with_writes_rescanned': files_with_writes,
        'audit_json_path': str(AUDIT_JSON),
        'errors': errs,
        'verdict': 'PASS' if not errs else 'FAIL',
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"SLC-F-MINOR-WRITE-SURFACES-AUDIT-V1 {out['verdict']} errors={len(errs)} rescanned_surfaces={total}")
    for e in errs:
        print(' -', e)
    return 0 if out['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
