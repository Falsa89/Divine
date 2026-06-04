#!/usr/bin/env python3
"""validate_deferred_store_asset_summary_v1"""
from __future__ import annotations
import json, sys
from pathlib import Path
ROOT = Path('/app')
PREFIX = 'PROJECT-DEFERRED-STORE-ASSET-SUMMARY'
TAG = 'PUBLIC_SYNC_TAG_v77_MEGA_RELEASE_ACCELERATION_26_FEEDBACK_AGGREGATION_TRIAGE_WRAP_v78_READINESS'
P = 'data/design/release_acceleration/deferred_store_asset_summary_v1.json'
M = 'data/design/release_acceleration/deferred_store_asset_summary_marker_v1.json'
REQUIRED_IDS = {'store_beta_readiness_apply','hero_asset_staging_import_and_resolver_super_pack','closed_alpha_actual_session_run'}

def fail(msg): print(f'{PREFIX}: FAIL {msg}'); sys.exit(1)

def main():
    for r in (P, M):
        if not (ROOT / r).exists(): fail(f'missing {r}')
    d = json.loads((ROOT / P).read_text()); m = json.loads((ROOT / M).read_text())
    if d.get('public_sync_tag') != TAG: fail('tag mismatch')
    lanes = d.get('deferred_lanes', [])
    ids = {l.get('id') for l in lanes}
    if not REQUIRED_IDS.issubset(ids): fail(f'lanes missing: {REQUIRED_IDS - ids}')
    for lane in lanes:
        if lane.get('action_v77') != 'no_action': fail(f'lane {lane.get("id")} action_v77 must be no_action')
    for k in ('store_upload_performed','play_console_changes_performed','appstore_connect_changes_performed','testflight_changes_performed','build_generation_performed','real_asset_import','asset_runtime_resolver_changed','broad_commercial_release'):
        if d.get(k) is not False: fail(f'{k} must be false')
    if d.get('db_writes') != 0: fail('db_writes must be 0')
    if m.get('store_upload_performed') is not False: fail('marker.store_upload_performed must be false')
    print(f'{PREFIX}: PASS')

if __name__ == '__main__': main()
