#!/usr/bin/env python3
"""Validator: PROJECT-EPHEMERAL-SIMULATION-INVARIANT-REPORT-DRY-RUN (v50 Track A)."""
from __future__ import annotations
import os, sys, json, re

ROOT = '/app'
UTIL = os.path.join(ROOT, 'backend/utils/economy_ephemeral_simulation_invariant_report_dry_run.py')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/ephemeral_simulation_invariant_report_dry_run_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(UTIL): fail(f'missing utility: {UTIL}')
else:
    src = open(UTIL).read()
    for needle in (
        'def build_invariant_report(',
        'def build_config_block(',
        'def _test_reset(',
        'CONTRACT_VERSION = "economy_ephemeral_simulation_invariant_report_dry_run_v1"',
        'DB_WRITES = 0',
        'REAL_DB_WRITES = 0',
        'PERSISTED = False',
        'LIVE_APPLY_ALLOWED = False',
        'LIVE_ENFORCEMENT_ENABLED = False',
        'PRODUCTION_DB_TOUCHED = False',
        'MONGO_URL_USED = False',
        'PYMONGO_USED = False',
        'MOTOR_USED = False',
        'ENV_READ = False',
        'FILESYSTEM_WRITES = 0',
        'NO_ROUTE_EXPOSURE = True',
        'NO_SERVER_PY_CHANGE = True',
    ):
        if needle not in src: fail(f'utility missing: {needle}')
    forbidden_active = (
        'import pymongo', 'from pymongo', 'import motor', 'from motor',
        'import redis', 'from redis',
        'os.environ[', 'os.environ.get', 'os.getenv(', 'load_dotenv',
        'MongoClient(', 'AsyncIOMotorClient(',
        'requests.post', 'requests.get', 'urllib.request.urlopen', 'smtplib',
    )
    for forbidden in forbidden_active:
        if forbidden in src: fail(f'utility forbidden active symbol: {forbidden}')
    if re.search(r"open\([^)]+,\s*['\"][wa]", src): fail('utility writes to filesystem (forbidden)')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('contract_version', 'economy_ephemeral_simulation_invariant_report_dry_run_v1'),
        ('track', 'A'),
        ('total_scenarios_expected', 72),
        ('operation_families_count', 8),
        ('scenarios_per_family', 9),
        ('db_writes', 0),
        ('real_db_writes', 0),
        ('production_db_touched', False),
        ('mongo_url_used', False),
        ('pymongo_used', False),
        ('motor_used', False),
        ('env_read', False),
        ('filesystem_writes', 0),
        ('persisted', False),
        ('live_apply_allowed', False),
        ('live_enforcement_enabled', False),
        ('preview_request_blocked', False),
        ('no_route_exposure', True),
        ('no_server_py_change', True),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v50_MEGA_ECONOMY_SAFETY_ACCELERATION_14'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

# Runtime self-test
if not FAILS:
    sys.path.insert(0, os.path.join(ROOT, 'backend'))
    try:
        from utils.economy_ephemeral_simulation_invariant_report_dry_run import (
            build_invariant_report, build_config_block, _test_reset,
        )
        _test_reset()
        cfg = build_config_block()
        for k, v in (
            ('enabled', True),
            ('contract_version', 'economy_ephemeral_simulation_invariant_report_dry_run_v1'),
            ('dry_run_only', True),
            ('operation_families_count', 8),
            ('scenarios_per_family', 9),
            ('db_writes', 0),
            ('real_db_writes', 0),
            ('production_db_touched', False),
            ('mongo_url_used', False),
            ('pymongo_used', False),
            ('motor_used', False),
            ('env_read', False),
            ('filesystem_writes', 0),
            ('live_apply_allowed', False),
            ('live_enforcement_enabled', False),
            ('preview_request_blocked', False),
            ('no_route_exposure', True),
            ('no_server_py_change', True),
        ):
            if cfg.get(k) != v: fail(f'config {k} != {v} (got {cfg.get(k)})')
        _test_reset()
        rep = build_invariant_report()
        for k, v in (
            ('enabled', True),
            ('contract_version', 'economy_ephemeral_simulation_invariant_report_dry_run_v1'),
            ('dry_run_only', True),
            ('operation_families_count', 8),
            ('scenarios_per_family', 9),
            ('total_scenarios_expected', 72),
            ('scenarios_evaluated', 72),
            ('all_invariants_ok', True),
            ('db_writes', 0),
            ('real_db_writes', 0),
            ('production_db_touched', False),
            ('mongo_url_used', False),
            ('pymongo_used', False),
            ('motor_used', False),
            ('env_read', False),
            ('filesystem_writes', 0),
            ('persisted', False),
            ('live_apply_allowed', False),
            ('live_enforcement_enabled', False),
            ('preview_request_blocked', False),
            ('no_route_exposure', True),
            ('no_server_py_change', True),
            ('pii_safe', True),
            ('raw_payload_captured', False),
        ):
            if rep.get(k) != v: fail(f'report {k} != {v} (got {rep.get(k)})')
        if int(rep.get('total_simulated_ephemeral_writes_count') or 0) <= 0:
            fail('report total_simulated_ephemeral_writes_count must be > 0')
        per_fam = rep.get('per_family') or []
        if len(per_fam) != 8: fail(f'report per_family len != 8 (got {len(per_fam)})')
        for entry in per_fam:
            if not entry.get('all_ok'): fail(f'per_family entry not all_ok: {entry.get("operation_family")}')
            if entry.get('real_db_writes') != 0: fail(f'per_family real_db_writes != 0: {entry.get("operation_family")}')
            if entry.get('production_db_touched') is not False: fail(f'per_family production_db_touched != False: {entry.get("operation_family")}')
            if entry.get('mongo_url_used') is not False: fail(f'per_family mongo_url_used != False: {entry.get("operation_family")}')
            if entry.get('pymongo_used') is not False: fail(f'per_family pymongo_used != False: {entry.get("operation_family")}')
            if entry.get('motor_used') is not False: fail(f'per_family motor_used != False: {entry.get("operation_family")}')
            if entry.get('env_read') is not False: fail(f'per_family env_read != False: {entry.get("operation_family")}')
            if entry.get('filesystem_writes') != 0: fail(f'per_family filesystem_writes != 0: {entry.get("operation_family")}')
            if entry.get('live_apply_allowed') is not False: fail(f'per_family live_apply_allowed != False: {entry.get("operation_family")}')
            if entry.get('scenarios_executed') != 9: fail(f'per_family scenarios_executed != 9: {entry.get("operation_family")}')
    except Exception as e:
        fail(f'runtime self-test error: {e}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-EPHEMERAL-SIMULATION-INVARIANT-REPORT-DRY-RUN validator')
    sys.exit(1)
print('[PASS] PROJECT-EPHEMERAL-SIMULATION-INVARIANT-REPORT-DRY-RUN validator')
sys.exit(0)
