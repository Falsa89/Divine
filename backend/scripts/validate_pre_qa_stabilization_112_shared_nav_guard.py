#!/usr/bin/env python3
"""Pre-QA Stabilization 112 — Shared nav guard validator."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
guard = open(os.path.join(R, 'frontend/src/utils/preQaNavGuard.ts')).read()
for t in ('PRE_QA_BLOCKED_PLAYER_ROUTES', 'PRE_QA_BLOCKED_CATEGORIES',
          'isRouteAllowedInPreQa', 'isCategoryAllowedInPreQa',
          'preQaUnsafeVisible', 'preQaDevQaVisible', 'preQaGachaUiVisible',
          'SELECTED_SERVER_REQUIRED_BLOCKER', 'PRE_QA_ROUTE_BLOCKED_TOKEN'):
    assert t in guard, f'shared nav guard missing {t}'
for route in ("'/pvp'", "'/battlepass'", "'/shop'", "'/vip'", "'/guild'",
              "'/gvg'", "'/raid'", "'/territory'", "'/plaza'", "'/dm'", "'/events'",
              "'/gacha'", "'/sanctuary'", "'/friends'", "'/level-sharing'",
              "'/cosmetics'", "'/exclusive-items'", "'/unique-items'",
              "'/artifacts'", "'/constellations'", "'/fragments'", "'/runes'",
              "'/affinity'", "'/mail'", "'/wallet'", "'/materials'"):
    assert route in guard, f'shared guard missing route literal: {route}'
home = open(os.path.join(R, 'frontend/app/(tabs)/home.tsx')).read()
assert 'preQaNavGuard' in home and 'isRouteAllowedInPreQa' in home
menu = open(os.path.join(R, 'frontend/app/(tabs)/menu.tsx')).read()
assert 'preQaNavGuard' in menu
print('[v112 PRE_QA_112_SHARED_NAV_GUARD] OK guard_present_with_canonical_routes home_menu_use_guard')
