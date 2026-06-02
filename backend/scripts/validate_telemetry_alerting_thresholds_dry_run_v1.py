#!/usr/bin/env python3
"""Validator: PROJECT-TELEMETRY-ALERTING-THRESHOLDS-DRY-RUN (v46 Track A)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
UTIL = os.path.join(ROOT, 'backend/utils/economy_telemetry_alerting_thresholds_dry_run.py')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/telemetry_alerting_thresholds_dry_run_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(UTIL): fail(f'missing utility: {UTIL}')
else:
    src = open(UTIL).read()
    for needle in (
        'def evaluate_alerts_from_snapshot(',
        'def build_alerting_thresholds_config(',
        'def _test_reset(',
        'DB_WRITES = 0',
        'PERSISTED = False',
        'LIVE_ENFORCEMENT_ENABLED = False',
        'PREVIEW_REQUEST_BLOCKED = False',
        'ALERT_SINK_LIVE_ENABLED = False',
        '"replay_rate": {"warn": 0.20, "critical": 0.50}',
        '"conflict_rate": {"warn": 0.05, "critical": 0.15}',
        '"missing_key_rate": {"warn": 0.10, "critical": 0.25}',
    ):
        if needle not in src: fail(f'utility missing: {needle}')
    for forbidden in ('import redis', 'pymongo', 'requests.post', 'urllib.request.urlopen', 'smtplib', 'open("/', "open('/"):
        if forbidden in src: fail(f'utility forbidden symbol: {forbidden}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    if m.get('contract_version') != 'economy_telemetry_alerting_thresholds_dry_run_v1': fail('marker contract_version mismatch')
    if m.get('alert_sink_live_enabled') is not False: fail('marker alert_sink_live_enabled != False')
    if m.get('alert_dispatched') is not False: fail('marker alert_dispatched != False')
    if m.get('external_sink_used') is not False: fail('marker external_sink_used != False')
    if m.get('db_writes') != 0: fail('marker db_writes != 0')
    if m.get('public_sync_tag') != 'PUBLIC_SYNC_TAG_v46_MEGA_ECONOMY_SAFETY_ACCELERATION_10': fail('marker public_sync_tag mismatch')

# Runtime self-test
if not FAILS:
    sys.path.insert(0, os.path.join(ROOT, 'backend'))
    try:
        from utils.economy_telemetry_alerting_thresholds_dry_run import (
            evaluate_alerts_from_snapshot, build_alerting_thresholds_config, _test_reset, THRESHOLDS,
        )
        cfg = build_alerting_thresholds_config()
        if not cfg.get('enabled'): fail('config not enabled')
        if cfg.get('alert_sink_live_enabled') is not False: fail('config alert_sink_live_enabled != False')
        if cfg.get('db_writes') != 0: fail('config db_writes != 0')
        if cfg.get('thresholds', {}).get('replay_rate', {}).get('critical') != 0.50: fail('config replay critical threshold mismatch')
        # No 60s window
        e0 = evaluate_alerts_from_snapshot({})
        if e0.get('evaluated') is not False: fail('empty snapshot must yield evaluated=False')
        if e0.get('alert_dispatched') is not False: fail('empty snapshot must have alert_dispatched=False')
        # OK case
        snap_ok = {'windows': [{'window_seconds': 60, 'total_events': 100, 'replay_same_hash_count': 5, 'conflict_diff_hash_count': 0, 'missing_key_count': 0}]}
        e1 = evaluate_alerts_from_snapshot(snap_ok)
        if e1.get('overall_level') != 'ok': fail(f'ok case wrong overall: {e1.get("overall_level")}')
        # Warn replay
        snap_warn = {'windows': [{'window_seconds': 60, 'total_events': 100, 'replay_same_hash_count': 25, 'conflict_diff_hash_count': 0, 'missing_key_count': 0}]}
        e2 = evaluate_alerts_from_snapshot(snap_warn)
        if e2.get('overall_level') != 'warn': fail(f'warn case wrong overall: {e2.get("overall_level")}')
        # Critical replay
        snap_crit = {'windows': [{'window_seconds': 60, 'total_events': 100, 'replay_same_hash_count': 60, 'conflict_diff_hash_count': 0, 'missing_key_count': 0}]}
        e3 = evaluate_alerts_from_snapshot(snap_crit)
        if e3.get('overall_level') != 'critical': fail(f'critical replay case wrong overall: {e3.get("overall_level")}')
        # Critical immediate: db_writes_observed_total > 0
        snap_dbw = {'windows': [{'window_seconds': 60, 'total_events': 100, 'replay_same_hash_count': 0, 'conflict_diff_hash_count': 0, 'missing_key_count': 0, 'db_writes_observed_total': 1}]}
        e4 = evaluate_alerts_from_snapshot(snap_dbw)
        if e4.get('overall_level') != 'critical': fail('critical_immediate db_writes did not trigger')
        if e4.get('critical_immediate_observed') is not True: fail('critical_immediate_observed not True')
        if e4.get('alert_dispatched') is not False: fail('alert_dispatched must always be False')
        # Reward grants observed -> critical
        snap_rg = {'windows': [{'window_seconds': 60, 'total_events': 5, 'reward_grants_observed_total': 2}]}
        e5 = evaluate_alerts_from_snapshot(snap_rg)
        if e5.get('overall_level') != 'critical': fail('critical_immediate reward_grants did not trigger')
    except Exception as e:
        fail(f'runtime self-test error: {e}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-TELEMETRY-ALERTING-THRESHOLDS-DRY-RUN validator')
    sys.exit(1)
print('[PASS] PROJECT-TELEMETRY-ALERTING-THRESHOLDS-DRY-RUN validator')
sys.exit(0)
