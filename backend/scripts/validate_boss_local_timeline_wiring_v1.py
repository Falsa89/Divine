#!/usr/bin/env python3
"""Validator: PROJECT-BOSS-LOCAL-TIMELINE-WIRING (v59 Track C).

Verifica:
- boss_local_timeline_wiring_contract_v1 + boss_delta_v59 + marker
- frontend/app/boss-visual-preview.tsx ha:
  * buildBossTimeline function
  * default seed boss-alpha-v59
  * stepIndex state + play/pause + cleanup timer
  * useEffect cleanup (timer)
  * no fetch / no /api/ use / no battle_engine() / no import combat/story / no reanimated / no Claim CTA
No fake PASS. No validator weakening.
"""
from __future__ import annotations
import os, sys, re, json

ROOT = '/app'
PACK = 'MEGA_RELEASE_ACCELERATION_8_LOCAL_TIMELINE_AND_RUNNER_PAYLOAD_CONTRACT_BATCH_PACK_v59'
TAG = 'PUBLIC_SYNC_TAG_v59_MEGA_RELEASE_ACCELERATION_8_LOCAL_TIMELINE_AND_RUNNER_PAYLOAD_CONTRACT_BATCH'
CONTRACT = os.path.join(ROOT, 'data/design/release_acceleration/boss_local_timeline_wiring_contract_v1.json')
DELTA = os.path.join(ROOT, 'data/design/release_acceleration/battle_entrypoint_registry_v2_boss_delta_v59.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/boss_local_timeline_wiring_marker_v1.json')
SCREEN = os.path.join(ROOT, 'frontend/app/boss-visual-preview.tsx')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(CONTRACT):
    fail(f'missing contract: {CONTRACT}')
else:
    c = json.load(open(CONTRACT))
    if c.get('version') != 'boss_local_timeline_wiring_contract_v1': fail('contract.version mismatch')
    if c.get('mode_id') != 'boss': fail('contract.mode_id mismatch')
    if c.get('previous_state') != 'preview_shell_v57': fail('contract.previous_state mismatch')
    if c.get('target_state') != 'local_dummy_seed_wired_v59': fail('contract.target_state mismatch')
    if c.get('default_seed') != 'boss-alpha-v59': fail('contract.default_seed mismatch')
    if c.get('timeline_steps_min') != 5: fail('contract.timeline_steps_min != 5')
    if c.get('timeline_steps_max') != 7: fail('contract.timeline_steps_max != 7')
    if c.get('db_writes') != 0: fail('contract.db_writes != 0')
    if c.get('battle_engine_runtime_used') is not False: fail('contract.battle_engine_runtime_used != False')
    if c.get('backend_used') is not False: fail('contract.backend_used != False')

if not os.path.exists(DELTA):
    fail(f'missing delta: {DELTA}')
else:
    d = json.load(open(DELTA))
    if d.get('version') != 'battle_entrypoint_registry_v2_boss_delta_v59': fail('delta.version mismatch')
    bd = (d.get('deltas') or {}).get('boss') or {}
    if bd.get('new_state') != 'local_dummy_seed_wired_v59': fail('delta.boss.new_state mismatch')
    if bd.get('new_implementation_tier') != 'local_timeline': fail('delta.boss.new_implementation_tier mismatch')
    om = d.get('other_modes_unchanged') or {}
    if om.get('material_raid') != 'alpha_loop_closed_v53': fail('delta.other_modes_unchanged.material_raid mismatch')
    if om.get('training') != 'local_dummy_seed_wired_v56': fail('delta.other_modes_unchanged.training mismatch')

if not os.path.exists(SCREEN):
    fail(f'missing screen: {SCREEN}')
else:
    src = open(SCREEN).read()
    if 'buildBossTimeline' not in src: fail('screen missing buildBossTimeline')
    if 'boss-alpha-v59' not in src: fail('screen missing boss-alpha-v59 seed')
    if 'stepIndex' not in src: fail('screen missing stepIndex state')
    if 'isPlaying' not in src or 'setIsPlaying' not in src: fail('screen missing play/pause state')
    if 'clearTimeout' not in src and 'clearInterval' not in src: fail('screen missing timer cleanup')
    if 'useEffect' not in src: fail('screen missing useEffect (cleanup)')
    if 'local_dummy_seed_wired_v59' not in src and 'local timeline' not in src.lower():
        fail('screen missing v59 state label')
    if 'SafeAreaView' not in src: fail('screen missing SafeAreaView')
    # forbidden patterns
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
        if re.search(pat, src):
            fail(f'screen forbidden {desc}')

if not os.path.exists(MARKER):
    fail(f'missing marker: {MARKER}')
else:
    mk = json.load(open(MARKER))
    if mk.get('marker_version') != 'boss_local_timeline_wiring_marker_v1': fail('marker.version mismatch')
    for k, v in (('pack',PACK),('public_sync_tag',TAG),('default_seed','boss-alpha-v59'),
                 ('timeline_steps_min',5),('timeline_steps_max',7),('deeplink_only',True),
                 ('calls_backend',False),('calls_battle_engine',False),
                 ('claim_button_present',False),('reward_grant_enabled',False),
                 ('reanimated_used',False),('combat_tsx_imported',False),
                 ('story_tsx_imported',False),('db_writes',0),
                 ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k) != v: fail(f'marker.{k} != {v} (got {mk.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-BOSS-LOCAL-TIMELINE-WIRING')
    sys.exit(1)
print('[PASS] PROJECT-BOSS-LOCAL-TIMELINE-WIRING')
sys.exit(0)
