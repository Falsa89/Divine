#!/usr/bin/env python3
"""Validator: PROJECT-EVENT-LOCAL-DUMMY-SEED-WIRING (v60 Track C)."""
from __future__ import annotations
import os, sys, re, json

ROOT = '/app'
PACK = 'MEGA_RELEASE_ACCELERATION_9_ROUTER_ADAPTER_EVENT_ARENA_LOCAL_TIMELINE_BATCH_PACK_v60'
TAG = 'PUBLIC_SYNC_TAG_v60_MEGA_RELEASE_ACCELERATION_9_ROUTER_ADAPTER_EVENT_ARENA_LOCAL_TIMELINE_BATCH'
CONTRACT = os.path.join(ROOT, 'data/design/release_acceleration/event_local_dummy_seed_wiring_contract_v1.json')
DELTA = os.path.join(ROOT, 'data/design/release_acceleration/battle_entrypoint_registry_v2_event_delta_v60.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/event_local_dummy_seed_wiring_marker_v1.json')
SCREEN = os.path.join(ROOT, 'frontend/app/event-visual-preview.tsx')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(CONTRACT):
    fail(f'missing contract: {CONTRACT}')
else:
    c = json.load(open(CONTRACT))
    if c.get('version') != 'event_local_dummy_seed_wiring_contract_v1': fail('contract.version mismatch')
    if c.get('mode_id') != 'event': fail('contract.mode_id mismatch')
    if c.get('previous_state') != 'preview_shell_v58': fail('contract.previous_state mismatch')
    if c.get('target_state') != 'local_dummy_seed_wired_v60': fail('contract.target_state mismatch')
    if c.get('default_seed') != 'event-alpha-v60': fail('contract.default_seed mismatch')
    if c.get('timeline_steps_min') != 5: fail('contract.timeline_steps_min')
    if c.get('timeline_steps_max') != 7: fail('contract.timeline_steps_max')
    if c.get('db_writes') != 0: fail('contract.db_writes')

if not os.path.exists(DELTA):
    fail(f'missing delta: {DELTA}')
else:
    d = json.load(open(DELTA))
    if d.get('version') != 'battle_entrypoint_registry_v2_event_delta_v60': fail('delta.version mismatch')
    ed = (d.get('deltas') or {}).get('event') or {}
    if ed.get('new_state') != 'local_dummy_seed_wired_v60': fail('delta.event.new_state mismatch')
    if ed.get('new_implementation_tier') != 'local_timeline': fail('delta.event.tier mismatch')

if not os.path.exists(SCREEN):
    fail(f'missing screen: {SCREEN}')
else:
    src = open(SCREEN).read()
    if 'buildEventTimeline' not in src: fail('screen missing buildEventTimeline')
    if 'event-alpha-v60' not in src: fail('screen missing event-alpha-v60 seed')
    if 'stepIndex' not in src: fail('screen missing stepIndex')
    if 'isPlaying' not in src or 'setIsPlaying' not in src: fail('screen missing play/pause')
    if 'clearTimeout' not in src: fail('screen missing clearTimeout cleanup')
    if 'useEffect' not in src: fail('screen missing useEffect cleanup')
    if 'SafeAreaView' not in src: fail('screen missing SafeAreaView')
    for pat, desc in [
        (r"from\s+['\"][^'\"]*combat['\"]", 'combat import'),
        (r"from\s+['\"][^'\"]*story['\"]", 'story import'),
        (r'react-native-reanimated', 'reanimated'),
        (r'\bfetch\s*\(', 'fetch call'),
        (r'\baxios\b', 'axios usage'),
        (r"['\"`(]/api/", '/api/ use'),
        (r'battle_engine\s*\(', 'battle_engine call'),
        (r"from\s+['\"][^'\"]*battle_engine", 'battle_engine import'),
        (r'>\s*Claim\s*<', 'Claim CTA'),
    ]:
        if re.search(pat, src): fail(f'screen forbidden {desc}')

if not os.path.exists(MARKER):
    fail(f'missing marker: {MARKER}')
else:
    mk = json.load(open(MARKER))
    if mk.get('marker_version') != 'event_local_dummy_seed_wiring_marker_v1': fail('marker.version mismatch')
    for k, v in (('pack',PACK),('public_sync_tag',TAG),('default_seed','event-alpha-v60'),
                 ('timeline_steps_min',5),('timeline_steps_max',7),('deeplink_only',True),
                 ('calls_backend',False),('calls_battle_engine',False),
                 ('claim_button_present',False),('reward_grant_enabled',False),
                 ('reanimated_used',False),('combat_tsx_imported',False),
                 ('story_tsx_imported',False),('db_writes',0),
                 ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k) != v: fail(f'marker.{k} != {v}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-EVENT-LOCAL-DUMMY-SEED-WIRING'); sys.exit(1)
print('[PASS] PROJECT-EVENT-LOCAL-DUMMY-SEED-WIRING'); sys.exit(0)
