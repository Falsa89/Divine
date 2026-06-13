#!/usr/bin/env python3
"""Pre-QA Stabilization 114 — Home routes canonicalization + dead-link guard."""
import os, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
guard_fp = os.path.join(R, 'frontend/src/utils/preQaNavGuard.ts')
guard = open(guard_fp).read()
home = open(os.path.join(R, 'frontend/app/(tabs)/home.tsx')).read()
manifest = open(os.path.join(R, 'frontend/constants/homeAssetsManifest.ts')).read()

# 1) preQaNavGuard normalizza /(tabs)/x -> /x.
assert 'normalizeRoute' in guard
assert 'export function normalizeRoute' in guard
assert '\\([^)]+\\)' in guard or '/\\(' in guard, 'normalizeRoute regex per /(group)/x missing'
assert 'isRouteAllowedInPreQa' in guard
# 2) isRouteAllowedInPreQa usa normalize.
m = re.search(r'export function isRouteAllowedInPreQa[^}]+\}', guard, re.DOTALL)
assert m is not None, 'isRouteAllowedInPreQa not found'
body = m.group(0)
assert 'normalizeRoute' in body, 'isRouteAllowedInPreQa must call normalizeRoute'
# 3) /(tabs)/gacha would be normalized to /gacha which is in blocked set.
assert "'/gacha'" in guard
# 4) Home hero tap /sanctuary guarded.
m2 = re.search(r'const onHeroTap[^}]+\}\s*;', home, re.DOTALL)
assert m2 is not None, 'onHeroTap not found'
hero_body = m2.group(0)
assert 'isRouteAllowedInPreQa' in hero_body and "'/sanctuary'" in hero_body
assert 'PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED' in hero_body
# 5) Missing home routes /quests, /arena, /blessings, /profile blocked.
for missing in ("'/quests'", "'/arena'", "'/blessings'", "'/profile'"):
    assert missing in guard, f'shared guard missing block for {missing}'
# 6) Pack 113 HomeOverflow fix preserved.
assert 'preQaNavGuard' in home
assert '_pushPreQaGuarded' in home
assert 'PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED' in home
# 7) HOME_ROUTES catalog still references /(tabs)/gacha (will be blocked via normalize).
assert "'/(tabs)/gacha'" in manifest or '/(tabs)/gacha' in manifest
# 8) Sanity: gacha tab still hidden (Pack 110 invariant).
layout = open(os.path.join(R, 'frontend/app/(tabs)/_layout.tsx')).read()
assert 'href: null' in layout and 'EXPO_PUBLIC_GACHA_UI_ENABLED' in layout
print('[v114 PRE_QA_114_HOME_ROUTES_CANONICALIZATION] OK normalizeRoute_present sanctuary_guarded missing_routes_blocked pack_113_preserved')
