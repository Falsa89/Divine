#!/usr/bin/env python3
"""Validator: PROJECT-EPHEMERAL-TEST-DB-LIVE-SIMULATION-DRY-RUN (v49 Track A)."""
from __future__ import annotations
import os, sys, json, re

ROOT = '/app'
UTIL = os.path.join(ROOT, 'backend/utils/economy_ephemeral_test_db_live_simulation_dry_run.py')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/ephemeral_test_db_live_simulation_dry_run_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(UTIL): fail(f'missing utility: {UTIL}')
else:
    src = open(UTIL).read()
    for needle in (
        'def run_simulation_scenario(',
        'def run_all_scenarios_for_family(',
        'def run_full_pre_flight(',
        'def build_config_block(',
        'def _test_reset(',
        'DB_WRITES = 0',
        'PERSISTED = False',
        'LIVE_APPLY_ALLOWED = False',
        'LIVE_ENFORCEMENT_ENABLED = False',
        'PRODUCTION_DB_TOUCHED = False',
        'MONGO_URL_USED = False',
        'PYMONGO_USED = False',
        'MOTOR_USED = False',
        'ENV_READ = False',
        'FILESYSTEM_WRITES = 0',
    ):
        if needle not in src: fail(f'utility missing: {needle}')
    # Absolutely forbidden imports/usages (active code patterns only — do NOT match docstring/var name negations)
    forbidden_active = (
        'import pymongo', 'from pymongo', 'import motor', 'from motor',
        'import redis', 'from redis',
        'os.environ[', 'os.environ.get', 'os.getenv(', 'getenv(', 'load_dotenv',
        'MongoClient(', 'AsyncIOMotorClient(',
        'requests.post', 'requests.get', 'urllib.request.urlopen', 'smtplib',
    )
    for forbidden in forbidden_active:
        if forbidden in src: fail(f'utility forbidden active symbol: {forbidden}')
    # No filesystem writes (no open with 'w' or 'a')
    if re.search(r"open\([^)]+,\s*['\"][wa]", src): fail('utility writes to filesystem (forbidden)')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('contract_version', 'economy_ephemeral_test_db_live_simulation_dry_run_v1'),
        ('real_db_writes', 0),
        ('db_writes', 0),
        ('production_db_touched', False),
        ('mongo_url_used', False),
        ('pymongo_used', False),
        ('motor_used', False),
        ('env_read', False),
        ('filesystem_writes', 0),
        ('persisted', False),
        ('live_apply_allowed', False),
        ('preview_request_blocked', False),
        ('in_memory_only', True),
        ('supported_families_count', 8),
        ('scenarios_count', 9),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v49_MEGA_ECONOMY_SAFETY_ACCELERATION_13'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

# Runtime self-test
if not FAILS:
    sys.path.insert(0, os.path.join(ROOT, 'backend'))
    try:
        from utils.economy_ephemeral_test_db_live_simulation_dry_run import (
            run_simulation_scenario, run_all_scenarios_for_family,
            run_full_pre_flight, build_config_block, _test_reset,
            SUPPORTED_FAMILIES, SCENARIOS, COLLECTIONS,
        )
        _test_reset()
        if len(SUPPORTED_FAMILIES) != 8: fail(f'SUPPORTED_FAMILIES len != 8: {len(SUPPORTED_FAMILIES)}')
        if len(SCENARIOS) != 9: fail(f'SCENARIOS len != 9: {len(SCENARIOS)}')
        if len(COLLECTIONS) < 11: fail(f'COLLECTIONS len < 11: {len(COLLECTIONS)}')
        cfg = build_config_block()
        if cfg.get('real_db_writes') != 0: fail('config real_db_writes != 0')
        if cfg.get('production_db_touched') is not False: fail('config production_db_touched != False')
        if cfg.get('mongo_url_used') is not False: fail('config mongo_url_used != False')
        if cfg.get('pymongo_used') is not False: fail('config pymongo_used != False')
        if cfg.get('motor_used') is not False: fail('config motor_used != False')
        if cfg.get('env_read') is not False: fail('config env_read != False')
        if cfg.get('filesystem_writes') != 0: fail('config filesystem_writes != 0')
        if cfg.get('live_apply_allowed') is not False: fail('config live_apply_allowed != False')
        # Single scenarios
        _test_reset()
        r1 = run_simulation_scenario('material_raid_claim', 'happy_path', {'user_id': 'u1', 'client_idempotency_key': 'ck1', 'expected_reward_hash': 'h1', 'expected_reward_table_version': 1})
        if not r1.get('ok'): fail(f'happy_path not ok: {r1}')
        if r1.get('real_db_writes') != 0: fail('happy_path real_db_writes != 0')
        if r1.get('production_db_touched') is not False: fail('happy_path production_db_touched != False')
        if r1.get('simulated_writes_delta', 0) < 1: fail('happy_path simulated_writes_delta < 1')
        r2 = run_simulation_scenario('material_raid_claim', 'happy_path', {'user_id': 'u1', 'client_idempotency_key': 'ck1', 'expected_reward_hash': 'h1', 'expected_reward_table_version': 1})
        if r2.get('ok'): fail('second happy_path same ck should NOT be ok (duplicate_ledger_key)')
        # Per family
        _test_reset()
        f1 = run_all_scenarios_for_family('material_raid_claim')
        if not f1.get('all_ok'): fail(f'run_all_scenarios_for_family not all_ok: {[(x.get("scenario"), x.get("ok")) for x in f1.get("results") or []]}')
        if f1.get('real_db_writes') != 0: fail('family real_db_writes != 0')
        if f1.get('production_db_touched') is not False: fail('family production_db_touched != False')
        # Full pre-flight
        pf = run_full_pre_flight()
        if not pf.get('overall_ok'): fail('run_full_pre_flight overall_ok != True')
        if pf.get('operation_families_count') != 8: fail('preflight operation_families_count != 8')
        if pf.get('scenarios_per_family') != 9: fail('preflight scenarios_per_family != 9')
        if pf.get('real_db_writes') != 0: fail('preflight real_db_writes != 0')
        if pf.get('production_db_touched') is not False: fail('preflight production_db_touched != False')
        if pf.get('live_apply_allowed') is not False: fail('preflight live_apply_allowed != False')
    except Exception as e:
        fail(f'runtime self-test error: {e}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-EPHEMERAL-TEST-DB-LIVE-SIMULATION-DRY-RUN validator')
    sys.exit(1)
print('[PASS] PROJECT-EPHEMERAL-TEST-DB-LIVE-SIMULATION-DRY-RUN validator')
sys.exit(0)
