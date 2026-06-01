#!/usr/bin/env python3
"""Validator: PROJECT-REPLAY-CONFLICT-TELEMETRY-DRY-RUN (v45 Track B).

Verifies:
- design JSON exists and is well-formed
- all 8 safety preview routes have wire-up:
  - import _V45_DRY_RUN_AVAILABLE
  - /config exposes observability_aggregation_dry_run
  - POST responses include replay_conflict_telemetry_dry_run
  - /peek-buffer includes aggregation_snapshot
- no endpoint path / feature flag / default 503 / safety flag changes
- no DB / Redis / filesystem / persistent ledger
"""
from __future__ import annotations
import os, sys, json, hashlib

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/economy_safety/replay_conflict_telemetry_dry_run_v1.json')
MARKER = os.path.join(ROOT, 'data/design/economy_safety/replay_conflict_telemetry_dry_run_marker_v1.json')

ROUTES = [
    'backend/routes/gem_socket_commit_safety_preview.py',
    'backend/routes/material_raid_claim_safety_preview.py',
    'backend/routes/gear_forge_fusion_safety_preview.py',
    'backend/routes/rune_scroll_talisman_safety_preview.py',
    'backend/routes/artifact_upgrade_safety_preview.py',
    'backend/routes/divine_weapon_upgrade_safety_preview.py',
    'backend/routes/battle_pass_claim_safety_preview.py',
    'backend/routes/mail_claim_safety_preview.py',
]

MD5_INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx': '45fcc9890b6b128c37088bc33aa54caf',
}

FAILS = []

def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    if d.get('contract_version') != 'replay_conflict_telemetry_dry_run_v1': fail('design contract_version mismatch')
    if d.get('db_writes') != 0: fail('design db_writes != 0')
    if d.get('persisted') is not False: fail('design persisted != False')
    if d.get('live_enforcement_enabled') is not False: fail('design live_enforcement_enabled != False')
    if d.get('preview_request_blocked') is not False: fail('design preview_request_blocked != False')
    if len(d.get('operation_families') or []) != 8: fail('design must list 8 operation_families')
    if d.get('response_envelope_key') != 'replay_conflict_telemetry_dry_run': fail('design response_envelope_key mismatch')
    if d.get('config_envelope_key') != 'observability_aggregation_dry_run': fail('design config_envelope_key mismatch')
    if d.get('peek_buffer_envelope_key') != 'aggregation_snapshot': fail('design peek_buffer_envelope_key mismatch')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    if m.get('public_sync_tag') != 'PUBLIC_SYNC_TAG_v45_MEGA_ECONOMY_SAFETY_ACCELERATION_9': fail('marker public_sync_tag mismatch')
    if m.get('endpoint_paths_changed') is not False: fail('marker endpoint_paths_changed != False')
    if m.get('feature_flags_changed') is not False: fail('marker feature_flags_changed != False')
    if m.get('default_503_changed') is not False: fail('marker default_503_changed != False')
    if m.get('safety_flags_changed') is not False: fail('marker safety_flags_changed != False')
    if m.get('server_py_changed') is not False: fail('marker server_py_changed != False')
    if m.get('frontend_changed') is not False: fail('marker frontend_changed != False')

for rel in ROUTES:
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p): fail(f'missing route: {rel}'); continue
    s = open(p).read()
    if '_V45_DRY_RUN_AVAILABLE' not in s: fail(f'{rel}: missing v45 import flag')
    if 'observability_aggregation_dry_run' not in s: fail(f'{rel}: missing /config observability_aggregation_dry_run key')
    if '"replay_conflict_telemetry_dry_run"' not in s: fail(f'{rel}: missing POST replay_conflict_telemetry_dry_run key')
    if '"aggregation_snapshot"' not in s: fail(f'{rel}: missing /peek-buffer aggregation_snapshot key')
    if 'import redis' in s: fail(f'{rel}: forbidden import redis')
    if 'pymongo' in s: fail(f'{rel}: forbidden pymongo direct usage')

for rel, expected in MD5_INVARIANTS.items():
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p): fail(f'missing invariant file: {rel}'); continue
    h = hashlib.md5(open(p, 'rb').read()).hexdigest()
    if h != expected: fail(f'MD5 mismatch: {rel} got {h} expected {expected}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-REPLAY-CONFLICT-TELEMETRY-DRY-RUN validator')
    sys.exit(1)
print('[PASS] PROJECT-REPLAY-CONFLICT-TELEMETRY-DRY-RUN validator')
sys.exit(0)
