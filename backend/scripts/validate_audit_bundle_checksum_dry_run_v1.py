#!/usr/bin/env python3
"""Validator: PROJECT-AUDIT-BUNDLE-CHECKSUM-DRY-RUN (v48 Track A)."""
from __future__ import annotations
import os, sys, json, re

ROOT = '/app'
UTIL = os.path.join(ROOT, 'backend/utils/economy_audit_bundle_checksum_dry_run.py')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/audit_bundle_checksum_dry_run_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(UTIL): fail(f'missing utility: {UTIL}')
else:
    src = open(UTIL).read()
    for needle in (
        'def build_audit_bundle_checksum(',
        'def build_config_block(',
        'def _test_reset(',
        'hashlib.sha256',
        'DB_WRITES = 0',
        'PERSISTED = False',
        'LIVE_APPLY_ALLOWED = False',
        'LIVE_ENFORCEMENT_ENABLED = False',
        'PREVIEW_REQUEST_BLOCKED = False',
    ):
        if needle not in src: fail(f'utility missing: {needle}')
    for forbidden in ('import redis', 'pymongo', 'requests.post', 'smtplib', 'open("/tmp', "open('/tmp"):
        if forbidden in src: fail(f'utility forbidden symbol: {forbidden}')
    # Must not write to filesystem (no file open with w/a mode at module level)
    if re.search(r"open\([^)]+,\s*['\"][wa]", src): fail('utility writes to filesystem (forbidden)')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    if m.get('contract_version') != 'economy_audit_bundle_checksum_dry_run_v1': fail('marker contract_version mismatch')
    if m.get('hash_algorithm') != 'sha256': fail('marker hash_algorithm != sha256')
    if m.get('db_writes') != 0: fail('marker db_writes != 0')
    if m.get('live_apply_allowed') is not False: fail('marker live_apply_allowed != False')
    if m.get('read_only') is not True: fail('marker read_only != True')
    if m.get('alert_dispatched') is not False: fail('marker alert_dispatched != False')
    if m.get('external_sink_used') is not False: fail('marker external_sink_used != False')
    if m.get('public_sync_tag') != 'PUBLIC_SYNC_TAG_v48_MEGA_ECONOMY_SAFETY_ACCELERATION_12': fail('marker public_sync_tag mismatch')

# Runtime self-test: checksum determinism
if not FAILS:
    sys.path.insert(0, os.path.join(ROOT, 'backend'))
    try:
        from utils.economy_audit_bundle_checksum_dry_run import (
            build_audit_bundle_checksum, build_config_block, _test_reset,
        )
        cfg = build_config_block()
        if not cfg.get('enabled'): fail('config not enabled')
        if cfg.get('db_writes') != 0: fail('config db_writes != 0')
        if cfg.get('live_apply_allowed') is not False: fail('config live_apply_allowed != False')
        if cfg.get('read_only') is not True: fail('config read_only != True')
        r1 = build_audit_bundle_checksum()
        r2 = build_audit_bundle_checksum()
        if r1.get('checksum_sha256') != r2.get('checksum_sha256'): fail('checksum NOT deterministic across calls')
        if not isinstance(r1.get('checksum_sha256'), str) or len(r1.get('checksum_sha256')) != 64: fail('checksum not a sha256 hex string')
        if r1.get('file_count') < 30: fail(f'file_count too low: {r1.get("file_count")}')
        if r1.get('db_writes') != 0: fail('checksum result db_writes != 0')
        if r1.get('live_apply_allowed') is not False: fail('checksum result live_apply_allowed != False')
        if r1.get('read_only') is not True: fail('checksum result read_only != True')
        if r1.get('alert_dispatched') is not False: fail('checksum result alert_dispatched != False')
        files = r1.get('included_files') or []
        if files != sorted(files): fail('included_files not lexicographically sorted')
        if 'backend/utils/economy_audit_bundle_checksum_dry_run.py' not in files: fail('utility itself not included in bundle')
        if not any(p.startswith('data/design/economy_safety/') for p in files): fail('no economy_safety design markers in bundle')
        if not any(p.startswith('backend/routes/') and p.endswith('_safety_preview.py') for p in files): fail('no safety preview routes in bundle')
    except Exception as e:
        fail(f'runtime self-test error: {e}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-AUDIT-BUNDLE-CHECKSUM-DRY-RUN validator')
    sys.exit(1)
print('[PASS] PROJECT-AUDIT-BUNDLE-CHECKSUM-DRY-RUN validator')
sys.exit(0)
