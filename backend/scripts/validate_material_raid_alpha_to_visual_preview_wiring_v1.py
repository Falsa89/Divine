#!/usr/bin/env python3
"""Validator: PROJECT-MATERIAL-RAID-ALPHA-TO-VISUAL-PREVIEW-WIRING (v52 Track C)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
SCREEN = os.path.join(ROOT, 'frontend/app/material-raid-alpha.tsx')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/material_raid_alpha_to_visual_preview_wiring_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(SCREEN): fail(f'missing screen: {SCREEN}')
else:
    s = open(SCREEN).read()
    for needle in (
        "from 'expo-router'",
        'useRouter',
        'Apri preview battaglia visuale',
        "'/material-raid-visual-preview'",
        'onOpenVisualPreview',
        'isValidBattlePreview',
        "alpha_battle_preview_ready",
        'battle_seed_preview',
    ):
        if needle not in s: fail(f'alpha screen missing needle: {needle}')
    # The visual button must be conditionally rendered.
    if 'isValidBattlePreview ? (' not in s and 'isValidBattlePreview && (' not in s:
        fail('alpha screen must conditionally render visual button on isValidBattlePreview')
    # No live claim wording introduced.
    for bad in ('Claim live', 'Riscuoti subito'):
        if bad in s: fail(f'alpha screen must not contain live claim ui: {bad}')
    # combat.tsx must not be touched by this wiring — verified at rollup level.

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('track', 'C'),
        ('patched_frontend_path', 'frontend/app/material-raid-alpha.tsx'),
        ('deeplink_target', '/material-raid-visual-preview'),
        ('button_label_it', 'Apri preview battaglia visuale'),
        ('hidden_when_backend_offline_or_invalid_preview', True),
        ('offline_fallback_preserved', True),
        ('live_claim_button_added', False),
        ('home_menu_wiring_added', False),
        ('combat_tsx_changed', False),
        ('db_writes', 0),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v52_MEGA_RELEASE_ACCELERATION_2_VISUAL_BATTLE_RUNNER_WIRING_FOR_MATERIAL_RAID_ALPHA'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-MATERIAL-RAID-ALPHA-TO-VISUAL-PREVIEW-WIRING validator')
    sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-ALPHA-TO-VISUAL-PREVIEW-WIRING validator')
sys.exit(0)
