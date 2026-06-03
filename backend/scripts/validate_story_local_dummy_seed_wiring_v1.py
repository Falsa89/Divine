#!/usr/bin/env python3
"""Validator: PROJECT-STORY-LOCAL-DUMMY-SEED-WIRING (v61 Track A+B)."""
from __future__ import annotations
import os, sys, re, json

ROOT = '/app'
PACK = 'MEGA_RELEASE_ACCELERATION_10_STORY_TIMELINE_ROUTER_HARDENING_RUNTIME_GATE_SUPER_PACK_v61'
TAG = 'PUBLIC_SYNC_TAG_v61_MEGA_RELEASE_ACCELERATION_10_STORY_TIMELINE_ROUTER_HARDENING_RUNTIME_GATE'
CONTRACT = os.path.join(ROOT, 'data/design/release_acceleration/story_local_dummy_seed_wiring_contract_v1.json')
DELTA = os.path.join(ROOT, 'data/design/release_acceleration/battle_entrypoint_registry_v2_story_delta_v61.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/story_local_dummy_seed_wiring_marker_v1.json')
SCREEN = os.path.join(ROOT, 'frontend/app/story-visual-preview.tsx')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(CONTRACT): fail(f'missing contract')
else:
    c = json.load(open(CONTRACT))
    if c.get('version') != 'story_local_dummy_seed_wiring_contract_v1': fail('contract.version mismatch')
    if c.get('mode_id') != 'story': fail('contract.mode_id')
    if c.get('previous_state') != 'preview_shell_v58': fail('contract.previous_state')
    if c.get('target_state') != 'local_dummy_seed_wired_v61': fail('contract.target_state')
    if c.get('default_seed') != 'story-alpha-v61': fail('contract.default_seed')
    if c.get('timeline_steps_min') != 5: fail('contract.timeline_steps_min')
    if c.get('timeline_steps_max') != 7: fail('contract.timeline_steps_max')
    if c.get('db_writes') != 0: fail('contract.db_writes')
    if c.get('backend_used') is not False: fail('contract.backend_used != False')
    if c.get('backend_preview_endpoint') is not None: fail('contract.backend_preview_endpoint not null')
    if c.get('story_runtime_used') is not False: fail('contract.story_runtime_used != False')
    if c.get('story_tsx_changed') is not False: fail('contract.story_tsx_changed != False')
    if c.get('api_story_battle_changed') is not False: fail('contract.api_story_battle_changed != False')

if not os.path.exists(DELTA): fail('missing delta')
else:
    d = json.load(open(DELTA))
    if d.get('version') != 'battle_entrypoint_registry_v2_story_delta_v61': fail('delta.version')
    sd = (d.get('deltas') or {}).get('story') or {}
    if sd.get('new_state') != 'local_dummy_seed_wired_v61': fail('delta.story.new_state')
    if sd.get('new_implementation_tier') != 'local_timeline': fail('delta.story.tier')

if not os.path.exists(SCREEN): fail('missing screen')
else:
    src = open(SCREEN).read()
    if 'buildStoryTimeline' not in src: fail('screen missing buildStoryTimeline')
    if 'story-alpha-v61' not in src: fail('screen missing story-alpha-v61 seed')
    if 'stepIndex' not in src: fail('screen missing stepIndex')
    if 'isPlaying' not in src or 'setIsPlaying' not in src: fail('screen missing play/pause')
    if 'clearTimeout' not in src: fail('screen missing clearTimeout')
    if 'useEffect' not in src: fail('screen missing useEffect')
    if 'SafeAreaView' not in src: fail('screen missing SafeAreaView')
    if 'story_runtime_used = false' not in src: fail('screen missing story_runtime_used guard')
    for pat, desc in [
        (r"from\s+['\"][^'\"]*combat['\"]", 'combat import'),
        (r"from\s+['\"]\.\./story['\"]", 'parent story import'),
        (r"from\s+['\"]\./story['\"]", 'sibling story import'),
        (r'react-native-reanimated', 'reanimated'),
        (r'\bfetch\s*\(', 'fetch call'),
        (r'\baxios\b', 'axios'),
        (r"['\"`(]/api/", '/api/ use'),
        (r'battle_engine\s*\(', 'battle_engine call'),
        (r"from\s+['\"][^'\"]*battle_engine", 'battle_engine import'),
        (r'>\s*Claim\s*<', 'Claim CTA'),
    ]:
        if re.search(pat, src): fail(f'screen forbidden {desc}')

if not os.path.exists(MARKER): fail('missing marker')
else:
    mk = json.load(open(MARKER))
    if mk.get('marker_version') != 'story_local_dummy_seed_wiring_marker_v1': fail('marker.version')
    for k, v in (('pack',PACK),('public_sync_tag',TAG),('default_seed','story-alpha-v61'),
                 ('timeline_steps_min',5),('timeline_steps_max',7),('deeplink_only',True),
                 ('calls_backend',False),('calls_battle_engine',False),
                 ('claim_button_present',False),('reward_grant_enabled',False),
                 ('reanimated_used',False),('combat_tsx_imported',False),
                 ('story_tsx_imported',False),('story_runtime_used',False),
                 ('story_tsx_changed',False),('api_story_battle_changed',False),
                 ('db_writes',0),('validator_weakening',False),('fake_pass',False)):
        if mk.get(k) != v: fail(f'marker.{k} != {v}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-STORY-LOCAL-DUMMY-SEED-WIRING'); sys.exit(1)
print('[PASS] PROJECT-STORY-LOCAL-DUMMY-SEED-WIRING'); sys.exit(0)
