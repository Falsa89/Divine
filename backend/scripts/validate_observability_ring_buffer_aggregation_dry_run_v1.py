#!/usr/bin/env python3
"""Validator: PROJECT-OBSERVABILITY-RING-BUFFER-AGGREGATION-DRY-RUN (v45 Track A).

Verifies:
- utility file exists and has the required public API
- rolling windows 60/300/900 are declared
- in-memory only / no Redis / no filesystem / no persistent ledger
- PII-safe / no raw payload
- record + snapshot + config_block + telemetry envelope reachable
- 0 db writes, no live enforcement, preview not blocked
- _test_reset() resets the in-memory ring buffer
"""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
UTIL = os.path.join(ROOT, 'backend/utils/economy_observability_aggregation_dry_run.py')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/observability_ring_buffer_aggregation_dry_run_marker_v1.json')

FAILS = []

def fail(msg): FAILS.append(msg)

if not os.path.exists(UTIL): fail(f'missing utility: {UTIL}')
else:
    src = open(UTIL).read()
    for needle in (
        'def record_telemetry_event(',
        'def build_aggregation_snapshot(',
        'def build_config_block(',
        'def build_replay_conflict_telemetry_envelope(',
        'def _test_reset(',
        'ROLLING_WINDOWS_SECONDS = (60, 300, 900)',
        'MAX_EVENTS = 4096',
        'DB_WRITES = 0',
        'PERSISTED = False',
        'LIVE_ENFORCEMENT_ENABLED = False',
        'PREVIEW_REQUEST_BLOCKED = False',
    ):
        if needle not in src: fail(f'utility missing: {needle}')
    for forbidden in ('import redis', 'open("/', "open('/", 'pymongo', 'motor.motor_asyncio'):
        if forbidden in src: fail(f'utility forbidden symbol: {forbidden}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    if m.get('contract_version') != 'economy_observability_aggregation_dry_run_v1': fail('marker contract_version mismatch')
    if m.get('db_writes') != 0: fail('marker db_writes != 0')
    if m.get('live_enforcement_enabled') is not False: fail('marker live_enforcement_enabled != False')
    if m.get('preview_request_blocked') is not False: fail('marker preview_request_blocked != False')
    if m.get('persisted') is not False: fail('marker persisted != False')
    if m.get('pii_safe') is not True: fail('marker pii_safe != True')
    if m.get('raw_payload_captured') is not False: fail('marker raw_payload_captured != False')
    if m.get('public_sync_tag') != 'PUBLIC_SYNC_TAG_v45_MEGA_ECONOMY_SAFETY_ACCELERATION_9': fail('marker public_sync_tag mismatch')
    if m.get('rolling_windows_seconds') != [60, 300, 900]: fail('marker rolling_windows_seconds mismatch')

# Runtime self-test
if not FAILS:
    sys.path.insert(0, os.path.join(ROOT, 'backend'))
    try:
        from utils.economy_observability_aggregation_dry_run import (
            record_telemetry_event, build_aggregation_snapshot, build_config_block,
            build_replay_conflict_telemetry_envelope, _test_reset,
        )
        _test_reset()
        cfg = build_config_block()
        if not cfg.get('enabled'): fail('config_block not enabled')
        if cfg.get('db_writes') != 0: fail('config_block db_writes != 0')
        if cfg.get('live_enforcement_enabled') is not False: fail('config_block live_enforcement_enabled != False')
        if cfg.get('preview_request_blocked') is not False: fail('config_block preview_request_blocked != False')
        if cfg.get('rolling_windows_seconds') != [60, 300, 900]: fail('config_block windows mismatch')
        eid = record_telemetry_event('material_raid_claim', detection_statuses=['new_key_preview', 'new_client_key_preview'], route_name='validate-claim-request')
        if not eid: fail('record_telemetry_event returned None')
        snap = build_aggregation_snapshot('material_raid_claim')
        if snap.get('db_writes') != 0: fail('snapshot db_writes != 0')
        if snap.get('persisted') is not False: fail('snapshot persisted != False')
        win60 = snap.get('windows', [{}])[0]
        if win60.get('total_events') != 1: fail('snapshot 60s total_events != 1 after 1 record')
        if win60.get('new_key_count') != 1: fail('snapshot new_key_count != 1')
        env = build_replay_conflict_telemetry_envelope('material_raid_claim', detection_statuses=['same_key_same_hash_replay_preview'], route_name='validate-claim-request')
        if env.get('db_writes') != 0: fail('telemetry envelope db_writes != 0')
        if env.get('live_enforcement_enabled') is not False: fail('telemetry envelope live_enforcement_enabled != False')
        if env.get('preview_request_blocked') is not False: fail('telemetry envelope preview_request_blocked != False')
        _test_reset()
        snap2 = build_aggregation_snapshot('material_raid_claim')
        if snap2.get('windows', [{}])[0].get('total_events') != 0: fail('_test_reset did not clear ring buffer')
    except Exception as e:
        fail(f'runtime self-test error: {e}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-OBSERVABILITY-RING-BUFFER-AGGREGATION-DRY-RUN validator')
    sys.exit(1)
print('[PASS] PROJECT-OBSERVABILITY-RING-BUFFER-AGGREGATION-DRY-RUN validator')
sys.exit(0)
