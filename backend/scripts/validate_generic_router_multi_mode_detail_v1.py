#!/usr/bin/env python3
"""Validator: PROJECT-GENERIC-ROUTER-MULTI-MODE-DETAIL (v58 Track C).

Verifica che frontend/app/visual-battle-preview-router.tsx contenga:
 - 4 blocchi condizionali mode === 'story'|'tower'|'event'|'arena'
 - testo 'preview_shell_v58'
 - i blocchi 'training' (v56) e 'boss' (v57) restano presenti (no regressione)
 - nessun import da story.tsx / combat.tsx, nessun fetch /api/, nessun battle_engine
 - nessun pulsante 'Claim' nel router
No fake PASS. No validator weakening.
"""
from __future__ import annotations
import os, sys, re, json

ROOT = '/app'
ROUTER = os.path.join(ROOT, 'frontend/app/visual-battle-preview-router.tsx')
FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(ROUTER):
    fail(f'missing router: {ROUTER}')
else:
    src = open(ROUTER).read()
    for m in ('story','tower','event','arena'):
        if f"mode === '{m}'" not in src:
            fail(f"missing conditional block mode === '{m}'")
    if src.count('preview_shell_v58') < 4:
        fail(f'preview_shell_v58 should appear >=4 times (got {src.count("preview_shell_v58")})')
    if "mode === 'training'" not in src:
        fail('regression: training conditional block removed')
    if "mode === 'boss'" not in src:
        fail('regression: boss conditional block removed')
    # forbidden patterns
    for pat, desc in [
        (r"from\s+['\"]\.\./story['\"]", 'import from story'),
        (r"from\s+['\"]\.\./combat['\"]", 'import from combat'),
        (r'\bfetch\s*\(', 'fetch call'),
        (r'\baxios\b', 'axios usage'),
        (r"['\"`(]/api/", '/api/ endpoint reference (use)'),
        (r'battle_engine\s*\(', 'battle_engine function call'),
        (r"from\s+['\"][^'\"]*battle_engine", 'battle_engine import'),
        (r'react-native-reanimated', 'reanimated usage'),
        (r'>\s*Claim\s*<', 'Claim CTA visible text'),
    ]:
        if re.search(pat, src):
            fail(f'router forbidden {desc} ({pat})')
    if 'useLocalSearchParams' not in src:
        fail('useLocalSearchParams not used')

marker = os.path.join(ROOT, 'data/design/release_acceleration/generic_router_multi_mode_detail_marker_v1.json')
if not os.path.exists(marker):
    fail(f'missing track C marker: {marker}')
else:
    mk = json.load(open(marker))
    if mk.get('marker_version') != 'generic_router_multi_mode_detail_marker_v1': fail('track C marker version mismatch')
    if mk.get('screen_path') != 'frontend/app/visual-battle-preview-router.tsx': fail('track C marker screen_path mismatch')
    if mk.get('deeplink_only') is not True: fail('track C marker deeplink_only != True')
    if mk.get('home_menu_mandatory_routing') is not False: fail('track C marker home_menu_mandatory_routing != False')
    if mk.get('calls_backend') is not False: fail('track C marker calls_backend != False')
    if mk.get('calls_battle_engine') is not False: fail('track C marker calls_battle_engine != False')
    if mk.get('claim_button_present') is not False: fail('track C marker claim_button_present != False')
    if mk.get('db_writes') != 0: fail('track C marker db_writes != 0')
    if mk.get('material_raid_behavior_unchanged') is not True: fail('track C marker material_raid_behavior_unchanged != True')
    if mk.get('training_behavior_unchanged') is not True: fail('track C marker training_behavior_unchanged != True')
    if mk.get('boss_behavior_unchanged') is not True: fail('track C marker boss_behavior_unchanged != True')
    md = mk.get('modes_detail_block_added') or []
    for m in ('story','tower','event','arena'):
        if m not in md: fail(f'track C marker missing mode {m} in modes_detail_block_added')
    if mk.get('shows_preview_shell_v58') is not True: fail('track C marker shows_preview_shell_v58 != True')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-GENERIC-ROUTER-MULTI-MODE-DETAIL')
    sys.exit(1)
print('[PASS] PROJECT-GENERIC-ROUTER-MULTI-MODE-DETAIL')
sys.exit(0)
