#!/usr/bin/env python3
"""Validator: PROJECT-GUIDE-CODEX-ONBOARDING-ALPHA-FOUNDATION (v51 Track E)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/release_acceleration/guide_codex_onboarding_alpha_foundation_v1.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/guide_codex_onboarding_alpha_foundation_marker_v1.json')
SCREEN = os.path.join(ROOT, 'frontend/app/alpha-guide.tsx')

REQUIRED_KEYS = {
    'material_raid', 'reward_preview_vs_claim', 'visual_battle_policy',
    'asset_placeholder_vs_final', 'qa_tester_instructions',
    'bug_report_severity', 'economy_safety_dry_run_vs_live',
}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    if d.get('contract_version') != 'guide_codex_onboarding_alpha_foundation_v1':
        fail('design contract_version mismatch')
    if d.get('frontend_screen_is_static') is not True: fail('frontend_screen_is_static must be true')
    if d.get('frontend_screen_is_deeplink_only') is not True: fail('frontend_screen_is_deeplink_only must be true')
    if d.get('frontend_screen_has_backend_dependency') is not False: fail('frontend_screen_has_backend_dependency must be false')
    if d.get('frontend_screen_has_home_menu_wiring') is not False: fail('frontend_screen_has_home_menu_wiring must be false')
    if d.get('frontend_screen_has_mutation') is not False: fail('frontend_screen_has_mutation must be false')
    if d.get('text_language') != 'it': fail('text_language must be it')
    entries = d.get('guide_entries') or []
    seen = {e.get('key') for e in entries}
    miss = REQUIRED_KEYS - seen
    if miss: fail(f'guide_entries missing keys: {sorted(miss)}')
    for e in entries:
        if e.get('required') is not True: fail(f'guide entry {e.get("key")} required != true')
        if not e.get('title_it'): fail(f'guide entry {e.get("key")} title_it missing')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('contract_version', 'guide_codex_onboarding_alpha_foundation_v1'),
        ('track', 'E'),
        ('guide_entries_count', 7),
        ('frontend_screen_path', 'frontend/app/alpha-guide.tsx'),
        ('frontend_screen_is_static', True),
        ('frontend_screen_is_deeplink_only', True),
        ('frontend_screen_has_backend_dependency', False),
        ('frontend_screen_has_home_menu_wiring', False),
        ('text_language', 'it'),
        ('db_writes', 0),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v51_MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

# Optional frontend screen — must exist since marker claims it present.
if not os.path.exists(SCREEN):
    fail(f'frontend screen declared present but missing: {SCREEN}')
else:
    s = open(SCREEN).read()
    if 'export default function AlphaGuideScreen' not in s:
        fail('alpha-guide.tsx missing default export AlphaGuideScreen')
    # No backend fetch in static guide.
    if 'fetch(' in s:
        fail('alpha-guide.tsx must not call backend (no fetch)')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-GUIDE-CODEX-ONBOARDING-ALPHA-FOUNDATION validator')
    sys.exit(1)
print('[PASS] PROJECT-GUIDE-CODEX-ONBOARDING-ALPHA-FOUNDATION validator')
sys.exit(0)
