#!/usr/bin/env python3
"""Validator: PROJECT-ALERT-HISTORY-RING-BUFFER-DRY-RUN (v47 Track A)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
UTIL = os.path.join(ROOT, 'backend/utils/economy_alert_history_ring_buffer_dry_run.py')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/alert_history_ring_buffer_dry_run_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(UTIL): fail(f'missing utility: {UTIL}')
else:
    src = open(UTIL).read()
    for needle in (
        'def record_alert_evaluation(',
        'def peek_alert_history(',
        'def build_config_block(',
        'def build_alert_history_record_envelope(',
        'def _test_reset(',
        'ROLLING_WINDOWS_SECONDS = (60, 300, 900)',
        'MAX_ENTRIES = 1024',
        'DB_WRITES = 0',
        'PERSISTED = False',
        'LIVE_ENFORCEMENT_ENABLED = False',
        'PREVIEW_REQUEST_BLOCKED = False',
        'ALERT_SINK_LIVE_ENABLED = False',
    ):
        if needle not in src: fail(f'utility missing: {needle}')
    for forbidden in ('import redis', 'pymongo', 'requests.post', 'urllib.request.urlopen', 'smtplib', 'open("/', "open('/"):
        if forbidden in src: fail(f'utility forbidden symbol: {forbidden}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    if m.get('contract_version') != 'economy_alert_history_ring_buffer_dry_run_v1': fail('marker contract_version mismatch')
    if m.get('db_writes') != 0: fail('marker db_writes != 0')
    if m.get('alert_sink_live_enabled') is not False: fail('marker alert_sink_live_enabled != False')
    if m.get('alert_dispatched') is not False: fail('marker alert_dispatched != False')
    if m.get('external_sink_used') is not False: fail('marker external_sink_used != False')
    if m.get('pii_safe') is not True: fail('marker pii_safe != True')
    if m.get('raw_payload_captured') is not False: fail('marker raw_payload_captured != False')
    if m.get('rolling_windows_seconds') != [60, 300, 900]: fail('marker windows mismatch')
    if m.get('buffer_capacity') != 1024: fail('marker buffer_capacity != 1024')
    if m.get('public_sync_tag') != 'PUBLIC_SYNC_TAG_v47_MEGA_ECONOMY_SAFETY_ACCELERATION_11': fail('marker public_sync_tag mismatch')

# Runtime self-test
if not FAILS:
    sys.path.insert(0, os.path.join(ROOT, 'backend'))
    try:
        from utils.economy_alert_history_ring_buffer_dry_run import (
            record_alert_evaluation, peek_alert_history, build_config_block,
            build_alert_history_record_envelope, _test_reset,
        )
        _test_reset()
        cfg = build_config_block()
        if not cfg.get('enabled'): fail('config not enabled')
        if cfg.get('alert_sink_live_enabled') is not False: fail('config alert_sink_live_enabled != False')
        if cfg.get('db_writes') != 0: fail('config db_writes != 0')
        if cfg.get('buffer_capacity') != 1024: fail('config buffer_capacity != 1024')
        # record ok then critical
        e1 = record_alert_evaluation('material_raid_claim', {'overall_level': 'ok', 'rates': {'replay_rate': 0.0, 'conflict_rate': 0.0, 'missing_key_rate': 0.0}, 'alerts': []}, 'validate-claim-request')
        if not e1: fail('record returned None')
        e2 = record_alert_evaluation('material_raid_claim', {'overall_level': 'critical', 'rates': {'replay_rate': 0.6, 'conflict_rate': 0.0, 'missing_key_rate': 0.0}, 'critical_immediate_observed': False, 'alerts': [{'metric': 'replay_rate', 'level': 'critical'}]}, 'validate-claim-request')
        if not e2: fail('record critical returned None')
        snap = peek_alert_history('material_raid_claim', limit=10)
        if snap.get('db_writes') != 0: fail('snap db_writes != 0')
        if snap.get('alert_dispatched') is not False: fail('snap dispatched != False')
        if snap.get('alert_sink_live_enabled') is not False: fail('snap sink_live != False')
        if snap.get('pii_safe') is not True: fail('snap pii_safe != True')
        if snap.get('raw_payload_captured') is not False: fail('snap raw_payload_captured != False')
        if snap.get('buffer_capacity') != 1024: fail('snap buffer_capacity != 1024')
        win60 = snap.get('windows', [{}])[0]
        if win60.get('window_seconds') != 60: fail('snap first window != 60')
        if win60.get('total_entries') != 2: fail(f'snap 60s total != 2 got {win60.get("total_entries")}')
        if win60.get('by_level', {}).get('ok') != 1: fail('snap by_level.ok != 1')
        if win60.get('by_level', {}).get('critical') != 1: fail('snap by_level.critical != 1')
        env = build_alert_history_record_envelope('material_raid_claim', {'overall_level': 'warn'}, 'validate-claim-request')
        if env.get('db_writes') != 0: fail('envelope db_writes != 0')
        if env.get('alert_dispatched') is not False: fail('envelope dispatched != False')
        if env.get('recorded_overall_level') != 'warn': fail('envelope recorded_overall_level wrong')
        _test_reset()
        snap2 = peek_alert_history('material_raid_claim', limit=10)
        if snap2.get('windows', [{}])[0].get('total_entries') != 0: fail('_test_reset did not clear')
    except Exception as e:
        fail(f'runtime self-test error: {e}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-ALERT-HISTORY-RING-BUFFER-DRY-RUN validator')
    sys.exit(1)
print('[PASS] PROJECT-ALERT-HISTORY-RING-BUFFER-DRY-RUN validator')
sys.exit(0)
