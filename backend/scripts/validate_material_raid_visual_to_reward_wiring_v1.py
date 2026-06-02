#!/usr/bin/env python3
"""Validator: PROJECT-MATERIAL-RAID-VISUAL-TO-REWARD-WIRING (v53 Track C)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
SCREEN = os.path.join(ROOT, 'frontend/app/material-raid-visual-preview.tsx')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/material_raid_visual_to_reward_wiring_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(SCREEN): fail(f'missing screen: {SCREEN}')
else:
    s = open(SCREEN).read()
    for needle in (
        'onOpenRewardPreview',
        "'/material-raid-reward-preview'",
        'Apri reward summary preview',
        'hasMinimumParams',
    ):
        if needle not in s: fail(f'visual-preview missing needle: {needle}')
    # Conditional render guard
    if 'hasMinimumParams ? (' not in s and 'hasMinimumParams && (' not in s:
        fail('visual-preview must conditionally render reward button on hasMinimumParams')
    # No live claim wording introduced.
    for bad in ('Claim live', 'Riscuoti subito', 'Riscatta reward'):
        if bad in s: fail(f'visual-preview must not contain live claim ui: {bad}')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('track', 'C'),
        ('patched_frontend_path', 'frontend/app/material-raid-visual-preview.tsx'),
        ('deeplink_target', '/material-raid-reward-preview'),
        ('button_label_it', 'Apri reward summary preview'),
        ('hidden_when_params_missing', True),
        ('preserves_back_button', True),
        ('live_claim_button_added', False),
        ('home_menu_wiring_added', False),
        ('combat_tsx_changed', False),
        ('db_writes', 0),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v53_MEGA_RELEASE_ACCELERATION_3_MATERIAL_RAID_ALPHA_LOOP_CLOSURE'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-MATERIAL-RAID-VISUAL-TO-REWARD-WIRING validator')
    sys.exit(1)
print('[PASS] PROJECT-MATERIAL-RAID-VISUAL-TO-REWARD-WIRING validator')
sys.exit(0)
