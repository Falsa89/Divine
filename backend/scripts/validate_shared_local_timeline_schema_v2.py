#!/usr/bin/env python3
"""Validator: PROJECT-SHARED-LOCAL-TIMELINE-SCHEMA-v2 (v59 Track B).

Verifica schema timeline locale v2 condiviso:
- design_only=true, local_only=true, backend_used=false, db_writes=0
- timeline_steps_min=5, timeline_steps_max=7, deterministic_from_seed=true
- compatible_modes contains training,boss,tower
- fields required
No fake PASS. No validator weakening.
"""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
PACK = 'MEGA_RELEASE_ACCELERATION_8_LOCAL_TIMELINE_AND_RUNNER_PAYLOAD_CONTRACT_BATCH_PACK_v59'
TAG = 'PUBLIC_SYNC_TAG_v59_MEGA_RELEASE_ACCELERATION_8_LOCAL_TIMELINE_AND_RUNNER_PAYLOAD_CONTRACT_BATCH'
SCHEMA = os.path.join(ROOT, 'data/design/release_acceleration/local_visual_preview_timeline_schema_v2.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/local_visual_preview_timeline_schema_v2_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(SCHEMA):
    fail(f'missing schema: {SCHEMA}')
else:
    s = json.load(open(SCHEMA))
    if s.get('version') != 'local_visual_preview_timeline_schema_v2': fail('schema.version mismatch')
    if s.get('pack') != PACK: fail('schema.pack mismatch')
    if s.get('public_sync_tag') != TAG: fail('schema.public_sync_tag mismatch')
    for k, v in (('design_only',True),('local_only',True),('backend_used',False),
                 ('battle_engine_runtime_used',False),('db_writes',0),
                 ('timeline_steps_min',5),('timeline_steps_max',7),
                 ('deterministic_from_seed',True)):
        if s.get(k) != v: fail(f'schema.{k} != {v} (got {s.get(k)})')
    modes = s.get('compatible_modes') or []
    for m in ('training','boss','tower'):
        if m not in modes: fail(f'schema.compatible_modes missing {m}')
    fields = s.get('fields') or []
    for f in ('step_index','actor_side','actor_label','action_key','target_label',
              'floating_text_preview','hp_delta_preview','pose_hint','vfx_hint',
              'duration_ms','phase_hint_optional','modifier_hint_optional','deterministic_from_seed'):
        if f not in fields: fail(f'schema.fields missing {f}')

if not os.path.exists(MARKER):
    fail(f'missing marker: {MARKER}')
else:
    mk = json.load(open(MARKER))
    if mk.get('marker_version') != 'local_visual_preview_timeline_schema_v2_marker_v1': fail('marker.version mismatch')
    for k, v in (('pack',PACK),('public_sync_tag',TAG),('design_only',True),
                 ('local_only',True),('backend_used',False),
                 ('battle_engine_runtime_used',False),('db_writes',0),
                 ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k) != v: fail(f'marker.{k} != {v} (got {mk.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-SHARED-LOCAL-TIMELINE-SCHEMA-v2')
    sys.exit(1)
print('[PASS] PROJECT-SHARED-LOCAL-TIMELINE-SCHEMA-v2')
sys.exit(0)
