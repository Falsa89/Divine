#!/usr/bin/env python3
"""Validator: PROJECT-LOCAL-TIMELINE-SCHEMA-v3-DELTA (v60 Track E)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
PACK = 'MEGA_RELEASE_ACCELERATION_9_ROUTER_ADAPTER_EVENT_ARENA_LOCAL_TIMELINE_BATCH_PACK_v60'
TAG = 'PUBLIC_SYNC_TAG_v60_MEGA_RELEASE_ACCELERATION_9_ROUTER_ADAPTER_EVENT_ARENA_LOCAL_TIMELINE_BATCH'
DELTA = os.path.join(ROOT, 'data/design/release_acceleration/local_visual_preview_timeline_schema_v3_delta.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/local_visual_preview_timeline_schema_v3_delta_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DELTA):
    fail(f'missing delta: {DELTA}')
else:
    d = json.load(open(DELTA))
    if d.get('version') != 'local_visual_preview_timeline_schema_v3_delta': fail('delta.version mismatch')
    if d.get('extends') != 'local_visual_preview_timeline_schema_v2': fail('delta.extends mismatch')
    if d.get('pack') != PACK: fail('delta.pack')
    if d.get('public_sync_tag') != TAG: fail('delta.tag')
    for k, v in (('design_only',True),('local_only',True),('backend_used',False),
                 ('battle_engine_runtime_used',False),('db_writes',0),
                 ('deterministic_from_seed',True),('timeline_steps_min',5),('timeline_steps_max',7)):
        if d.get(k) != v: fail(f'delta.{k} != {v} (got {d.get(k)})')
    modes = d.get('compatible_modes') or []
    for m in ('training','boss','tower','event','arena'):
        if m not in modes: fail(f'delta.compatible_modes missing {m}')
    nof = d.get('new_optional_fields') or []
    for f in ('event_rule_hint_optional','arena_ruleset_hint_optional','bracket_hint_optional'):
        if f not in nof: fail(f'delta.new_optional_fields missing {f}')

if not os.path.exists(MARKER):
    fail(f'missing marker: {MARKER}')
else:
    mk = json.load(open(MARKER))
    if mk.get('marker_version') != 'local_visual_preview_timeline_schema_v3_delta_marker_v1': fail('marker.version mismatch')
    for k, v in (('pack',PACK),('public_sync_tag',TAG),('design_only',True),
                 ('local_only',True),('backend_used',False),
                 ('battle_engine_runtime_used',False),('db_writes',0),
                 ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k) != v: fail(f'marker.{k} != {v}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-LOCAL-TIMELINE-SCHEMA-v3-DELTA'); sys.exit(1)
print('[PASS] PROJECT-LOCAL-TIMELINE-SCHEMA-v3-DELTA'); sys.exit(0)
