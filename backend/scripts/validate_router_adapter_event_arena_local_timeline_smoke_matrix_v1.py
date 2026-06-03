#!/usr/bin/env python3
"""Validator: PROJECT-ROUTER-ADAPTER-EVENT-ARENA-LOCAL-TIMELINE-SMOKE-MATRIX (v60 Track F)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
PACK = 'MEGA_RELEASE_ACCELERATION_9_ROUTER_ADAPTER_EVENT_ARENA_LOCAL_TIMELINE_BATCH_PACK_v60'
TAG = 'PUBLIC_SYNC_TAG_v60_MEGA_RELEASE_ACCELERATION_9_ROUTER_ADAPTER_EVENT_ARENA_LOCAL_TIMELINE_BATCH'
MATRIX = os.path.join(ROOT, 'data/design/qa/router_adapter_event_arena_local_timeline_smoke_matrix_v1.json')
MARKER = os.path.join(ROOT, 'data/design/qa/router_adapter_event_arena_local_timeline_smoke_matrix_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(MATRIX):
    fail(f'missing matrix: {MATRIX}')
else:
    mx = json.load(open(MATRIX))
    if mx.get('version') != 'router_adapter_event_arena_local_timeline_smoke_matrix_v1': fail('matrix.version mismatch')
    if mx.get('pack') != PACK: fail('matrix.pack')
    if mx.get('public_sync_tag') != TAG: fail('matrix.tag')
    if mx.get('db_writes') != 0: fail('matrix.db_writes')
    flows = mx.get('flows') or []
    if len(flows) < 20: fail(f'matrix.flows too low: {len(flows)}')
    sevs = {f.get('severity') for f in flows}
    for s in ('P0','P1','P2','P3'):
        if s not in sevs: fail(f'matrix missing severity {s}')
    fb = mx.get('forbidden') or {}
    for k in ('claim_button_present','db_writes_nonzero','backend_fetch_present',
              'battle_engine_called','story_tsx_modified','story_battle_endpoint_called',
              'battle_simulate_endpoint_called','guild_war_policy_regression',
              'validator_weakening','fake_pass'):
        if fb.get(k) is not False: fail(f'matrix.forbidden.{k} != False')

if not os.path.exists(MARKER):
    fail(f'missing marker: {MARKER}')
else:
    mk = json.load(open(MARKER))
    if mk.get('marker_version') != 'router_adapter_event_arena_local_timeline_smoke_matrix_marker_v1': fail('marker.version mismatch')
    for k, v in (('pack',PACK),('public_sync_tag',TAG),('db_writes',0),
                 ('claim_button_present',False),('battle_engine_called',False),
                 ('backend_fetch_present',False),('story_tsx_modified',False),
                 ('guild_war_policy_regression',False),
                 ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k) != v: fail(f'marker.{k} != {v}')
    sev = mk.get('severity_levels') or []
    for s in ('P0','P1','P2','P3'):
        if s not in sev: fail(f'marker missing severity {s}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-ROUTER-ADAPTER-EVENT-ARENA-LOCAL-TIMELINE-SMOKE-MATRIX'); sys.exit(1)
print('[PASS] PROJECT-ROUTER-ADAPTER-EVENT-ARENA-LOCAL-TIMELINE-SMOKE-MATRIX'); sys.exit(0)
