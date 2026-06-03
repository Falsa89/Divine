#!/usr/bin/env python3
"""Validator: PROJECT-MASTER-RELEASE-ACCELERATION-ROADMAP (v54 Track A)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
ROADMAP = os.path.join(ROOT, 'data/design/release_acceleration/master_release_acceleration_roadmap_v1.json')
GRAPH = os.path.join(ROOT, 'data/design/release_acceleration/master_release_acceleration_dependency_graph_v1.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/master_release_acceleration_roadmap_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v54_MEGA_RELEASE_ACCELERATION_MASTER_BATCH_EXECUTION_PLAN'

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(ROADMAP): fail(f'missing roadmap: {ROADMAP}')
else:
    r = json.load(open(ROADMAP))
    if r.get('public_sync_tag') != TAG: fail(f'roadmap public_sync_tag != {TAG}')
    if r.get('option') != 'B_maximum_safe_acceleration': fail('roadmap option mismatch')
    pol = r.get('policy') or {}
    if pol.get('db_writes') != 0: fail('roadmap policy.db_writes != 0')
    if pol.get('live_apply_allowed') is not False: fail('roadmap policy.live_apply_allowed != false')
    if pol.get('reward_grant_enabled') is not False: fail('roadmap policy.reward_grant_enabled != false')
    if pol.get('stop_on_gate_failure') is not True: fail('roadmap policy.stop_on_gate_failure != true')
    batches = r.get('batches') or []
    ids = [b.get('id') for b in batches]
    expected_ids = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8']
    if ids != expected_ids: fail(f'roadmap batches ids mismatch: {ids}')
    for b in batches:
        for k in ('id', 'name', 'dependencies', 'risk_tier', 'can_execute_now', 'requires_manual_approval', 'stop_gate', 'validators', 'smoke', 'rollback'):
            if k not in b: fail(f'roadmap batch {b.get("id")} missing field {k}')
    deferred = set(r.get('high_risk_batches_deferred') or [])
    if deferred != {'B7', 'B8'}: fail(f'roadmap high_risk_batches_deferred != B7,B8 got {sorted(deferred)}')
    low = set(r.get('low_risk_batches_now') or [])
    if low != {'B1','B2','B3','B4','B5','B6'}: fail(f'roadmap low_risk_batches_now != B1..B6 got {sorted(low)}')

if not os.path.exists(GRAPH): fail(f'missing graph: {GRAPH}')
else:
    g = json.load(open(GRAPH))
    if g.get('public_sync_tag') != TAG: fail('graph public_sync_tag mismatch')
    nodes = {n.get('id') for n in (g.get('nodes') or [])}
    needed = {'v53','B1','B2','B3','B4','B5','B6','B7','B8'}
    if not needed.issubset(nodes): fail(f'graph missing nodes: {sorted(needed - nodes)}')
    edges = g.get('edges') or []
    if not any(e.get('from')=='v53' and e.get('to')=='B1' for e in edges):
        fail('graph missing edge v53->B1')
    stop = g.get('stop_gates') or {}
    for gid in ('GATE_0','GATE_1','GATE_2'):
        if gid not in stop: fail(f'graph stop_gates missing {gid}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('marker_version', 'master_release_acceleration_roadmap_marker_v1'),
        ('track', 'A'),
        ('public_sync_tag', TAG),
        ('batches_total', 8),
        ('runtime_wired', False),
        ('db_writes', 0),
        ('validator_weakening', False),
        ('fake_pass', False),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-MASTER-RELEASE-ACCELERATION-ROADMAP validator')
    sys.exit(1)
print('[PASS] PROJECT-MASTER-RELEASE-ACCELERATION-ROADMAP validator')
sys.exit(0)
