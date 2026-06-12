#!/usr/bin/env python3
"""Pre-QA Stabilization 110 — Menu cleanup validator."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
menu = open(os.path.join(R, 'frontend/app/(tabs)/menu.tsx')).read()
# Pre-QA Stabilization 112 accept either inline literal OR shared guard import.
_has_inline = 'EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE' in menu
_has_shared_guard = 'preQaNavGuard' in menu and 'preQaUnsafeVisible' in menu
assert _has_inline or _has_shared_guard, 'menu.tsx missing flag literal AND shared nav guard import'
_has_inline_routes = '_PRE_QA_BLOCKED_ROUTES' in menu
_has_shared_routes = 'PRE_QA_BLOCKED_PLAYER_ROUTES' in menu
assert _has_inline_routes or _has_shared_routes, 'menu.tsx missing blocked routes set'
_has_inline_cats = '_PRE_QA_BLOCKED_CATEGORIES' in menu
_has_shared_cats = 'PRE_QA_BLOCKED_CATEGORIES' in menu
assert _has_inline_cats or _has_shared_cats, 'menu.tsx missing blocked categories set'
# Shared guard file presence + sentinel routes.
if _has_shared_guard:
    g = open(os.path.join(R, 'frontend/src/utils/preQaNavGuard.ts')).read()
    for r in ("'/pvp'", "'/battlepass'", "'/item-shop'", "'/shop'", "'/vip'", "'/guild'",
              "'/gvg'", "'/raid'", "'/territory'", "'/plaza'", "'/dm'", "'/events'"):
        assert r in g, f'shared nav guard missing: {r}'
else:
    for r in ("'/pvp'", "'/battlepass'", "'/item-shop'", "'/shop'", "'/vip'", "'/guild'",
              "'/gvg'", "'/raid'", "'/territory'", "'/plaza'", "'/dm'", "'/events'"):
        assert r in menu, f'route not blocklisted: {r}'
for c in ('Playability & Announcements QA', 'Modalit'):
    assert c in menu, f'QA category not blocklisted: {c}'
# Frontend env: default OFF (anche se file assente).
import re
env_path = os.path.join(R, 'frontend/.env')
env = open(env_path).read() if os.path.exists(env_path) else ''
for f in ('EXPO_PUBLIC_GACHA_UI_ENABLED', 'EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE',
          'EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE'):
    if not env:
        # Assenza file = default OFF: accettato come safe-by-default.
        continue
    line_pattern = re.compile(rf'^{re.escape(f)}=(\S+)', re.MULTILINE)
    m = line_pattern.search(env)
    if m:
        assert m.group(1).strip().lower() in ('false', '0', 'no', 'off', ''), f'{f} not default OFF: {m.group(1)}'
print('[v110 PRE_QA_110_MENU_CLEANUP] OK twelve_routes_blocked qa_categories_hidden flags_default_off')
