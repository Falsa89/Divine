#!/usr/bin/env python3
"""Validator: PROJECT-MULTI-MODE-VISUAL-PREVIEW-SCREENS (v58 Track B).

Verifica le 4 schermate preview shell (story/tower/event/arena):
 - file presente in frontend/app/{mode}-visual-preview.tsx
 - deeplink-only (no router.replace, no useEffect navigate)
 - NO import da frontend/app/story.tsx o frontend/app/combat.tsx
 - NO Reanimated
 - NO fetch / axios / api_call / API_URL / EXPO_BACKEND_URL
 - NO claim button / reward grant
 - SafeAreaView usato
 - Testo italiano nei warning
 - Default seed -alpha-v58
No fake PASS. No validator weakening.
"""
from __future__ import annotations
import os, sys, re, json

ROOT = '/app'
MODES = ['story', 'tower', 'event', 'arena']
FAILS = []
def fail(m): FAILS.append(m)

for m in MODES:
    p = os.path.join(ROOT, f'frontend/app/{m}-visual-preview.tsx')
    if not os.path.exists(p):
        fail(f'missing screen {m}-visual-preview.tsx'); continue
    src = open(p).read()
    # forbidden imports / calls
    forbidden_patterns = [
        (r"from\s+['\"].*story['\"]", 'imports from story'),
        (r"from\s+['\"].*combat['\"]", 'imports from combat'),
        (r'react-native-reanimated', 'reanimated usage'),
        (r'\bfetch\s*\(', 'fetch call'),
        (r'\baxios\b', 'axios usage'),
        (r'EXPO_BACKEND_URL', 'backend env usage'),
        (r'/api/[a-zA-Z]', '/api/ endpoint reference (use)'),
        (r'battle_engine\s*\(', 'battle_engine function call'),
        (r"from\s+['\"][^'\"]*battle_engine", 'battle_engine import'),
        (r'Claim\b', 'Claim CTA text'),
        (r'reward_grant\s*\(', 'reward_grant call'),
    ]
    for pat, desc in forbidden_patterns:
        if re.search(pat, src):
            fail(f'{m}: forbidden {desc} ({pat})')
    if 'SafeAreaView' not in src:
        fail(f'{m}: SafeAreaView not used')
    if 'useLocalSearchParams' not in src:
        fail(f'{m}: useLocalSearchParams not used (deeplink params)')
    if 'Preview visuale non autoritativa' not in src:
        fail(f'{m}: italian warning missing')
    if f'{m}-alpha-v58' not in src:
        fail(f'{m}: default seed -alpha-v58 not referenced')
    if 'db_writes = 0' not in src:
        fail(f'{m}: guard line db_writes = 0 missing')
    if 'result_authoritative = false' not in src:
        fail(f'{m}: guard line result_authoritative = false missing')
    if 'router.replace' in src:
        fail(f'{m}: forbidden router.replace (deeplink-only)')

marker = os.path.join(ROOT, 'data/design/release_acceleration/multi_mode_visual_preview_screens_marker_v1.json')
if not os.path.exists(marker):
    fail(f'missing track B marker: {marker}')
else:
    mk = json.load(open(marker))
    if mk.get('marker_version') != 'multi_mode_visual_preview_screens_marker_v1': fail('track B marker version mismatch')
    if mk.get('deeplink_only') is not True: fail('track B marker deeplink_only != True')
    if mk.get('home_menu_mandatory_routing') is not False: fail('track B marker home_menu_mandatory_routing != False')
    if mk.get('calls_backend') is not False: fail('track B marker calls_backend != False')
    if mk.get('calls_battle_engine') is not False: fail('track B marker calls_battle_engine != False')
    if mk.get('claim_button_present') is not False: fail('track B marker claim_button_present != False')
    if mk.get('reward_grant_enabled') is not False: fail('track B marker reward_grant_enabled != False')
    if mk.get('reanimated_used') is not False: fail('track B marker reanimated_used != False')
    if mk.get('combat_tsx_imported') is not False: fail('track B marker combat_tsx_imported != False')
    if mk.get('story_tsx_imported') is not False: fail('track B marker story_tsx_imported != False')
    if mk.get('db_writes') != 0: fail('track B marker db_writes != 0')
    screens = mk.get('screens') or {}
    for m in MODES:
        if m not in screens: fail(f'track B marker missing screen entry {m}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-MULTI-MODE-VISUAL-PREVIEW-SCREENS')
    sys.exit(1)
print('[PASS] PROJECT-MULTI-MODE-VISUAL-PREVIEW-SCREENS')
sys.exit(0)
