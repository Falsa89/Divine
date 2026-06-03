#!/usr/bin/env python3
"""Validator: PROJECT-LOCAL-TIMELINE-SCHEMA-v4-DELTA (v61 Track E)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
PACK = 'MEGA_RELEASE_ACCELERATION_10_STORY_TIMELINE_ROUTER_HARDENING_RUNTIME_GATE_SUPER_PACK_v61'
TAG = 'PUBLIC_SYNC_TAG_v61_MEGA_RELEASE_ACCELERATION_10_STORY_TIMELINE_ROUTER_HARDENING_RUNTIME_GATE'
DELTA = os.path.join(ROOT, 'data/design/release_acceleration/local_visual_preview_timeline_schema_v4_delta.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/local_visual_preview_timeline_schema_v4_delta_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DELTA): fail('missing delta')
else:
    d = json.load(open(DELTA))
    if d.get('version') != 'local_visual_preview_timeline_schema_v4_delta': fail('delta.version')
    if d.get('extends') != 'local_visual_preview_timeline_schema_v3_delta': fail('delta.extends')
    for k, v in (('design_only',True),('local_only',True),('backend_used',False),
                 ('battle_engine_runtime_used',False),('db_writes',0),
                 ('deterministic_from_seed',True),('timeline_steps_min',5),('timeline_steps_max',7)):
        if d.get(k) != v: fail(f'delta.{k} != {v}')
    modes = d.get('compatible_modes') or []
    for m in ('training','boss','tower','event','arena','story'):
        if m not in modes: fail(f'delta.compatible_modes missing {m}')
    nof = d.get('new_optional_fields') or []
    for f in ('story_tutorial_hint_optional','story_faction_hint_optional','chapter_node_hint_optional'):
        if f not in nof: fail(f'delta.new_optional_fields missing {f}')

if not os.path.exists(MARKER): fail('missing marker')
else:
    mk = json.load(open(MARKER))
    if mk.get('marker_version') != 'local_visual_preview_timeline_schema_v4_delta_marker_v1': fail('marker.version')
    for k, v in (('pack',PACK),('public_sync_tag',TAG),('design_only',True),
                 ('local_only',True),('backend_used',False),
                 ('battle_engine_runtime_used',False),('db_writes',0),
                 ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k) != v: fail(f'marker.{k} != {v}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-LOCAL-TIMELINE-SCHEMA-v4-DELTA'); sys.exit(1)
print('[PASS] PROJECT-LOCAL-TIMELINE-SCHEMA-v4-DELTA'); sys.exit(0)
