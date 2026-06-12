#!/usr/bin/env python3
"""Pre-QA Stabilization 110 — Menu cleanup validator."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
menu = open(os.path.join(R, 'frontend/app/(tabs)/menu.tsx')).read()
assert 'EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE' in menu
assert '_PRE_QA_BLOCKED_ROUTES' in menu
assert '_PRE_QA_BLOCKED_CATEGORIES' in menu
for r in ("'/pvp'", "'/battlepass'", "'/item-shop'", "'/shop'", "'/vip'", "'/guild'",
          "'/gvg'", "'/raid'", "'/territory'", "'/plaza'", "'/dm'", "'/events'"):
    assert r in menu, f'route not blocklisted: {r}'
for c in ('Playability & Announcements QA', 'Modalit'):
    assert c in menu, f'QA category not blocklisted: {c}'
# Frontend env: default OFF.
import re
env = open(os.path.join(R, 'frontend/.env')).read()
for f in ('EXPO_PUBLIC_GACHA_UI_ENABLED=false', 'EXPO_PUBLIC_MENU_LEGACY_UNSAFE_VISIBLE=false',
          'EXPO_PUBLIC_DEV_QA_SURFACES_VISIBLE=false'):
    assert f in env, f'frontend/.env missing: {f}'
print('[v110 PRE_QA_110_MENU_CLEANUP] OK twelve_routes_blocked qa_categories_hidden flags_default_off')
