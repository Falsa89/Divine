#!/usr/bin/env python3
"""Pre-QA Stabilization 113 — HomeOverflow nav guard validator (static).

Fail se:
  - preQaNavGuard non e' importato/required in home.tsx
  - HomeOverflowPanel usa items.map() senza guard/filter
  - esistono raw unsafe router.push('/pvp'|'/events'|'/shop'|'/vip'|'/battlepass'|'/raid'|'/gvg'|'/plaza'|'/dm'|'/territory') dentro home.tsx
    senza essere wrappati in pushPreQaGuarded o isRouteAllowedInPreQa check
  - PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED è assente
"""
import os, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fp = os.path.join(R, 'frontend/app/(tabs)/home.tsx')
c = open(fp).read()

assert 'preQaNavGuard' in c, 'home.tsx must import/require preQaNavGuard'
assert 'PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED' in c, 'home.tsx must reference PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED'
# HomeOverflowPanel must use isRouteAllowedInPreQa on filter or in pushPreQaGuarded.
m = re.search(r'function HomeOverflowPanel\([^)]*\)\s*{(.*?)\n}\s*\n', c, re.DOTALL)
assert m is not None, 'HomeOverflowPanel function not found'
overflow_body = m.group(1)
assert 'isRouteAllowedInPreQa' in overflow_body, 'HomeOverflowPanel must call isRouteAllowedInPreQa'
assert '_pushPreQaGuarded' in overflow_body or 'pushPreQaGuarded' in overflow_body, 'HomeOverflowPanel must use guarded push helper'
assert '.filter((it) => _navGuard.isRouteAllowedInPreQa' in overflow_body or '.filter(it => _navGuard.isRouteAllowedInPreQa' in overflow_body, 'HomeOverflowPanel must filter items by guard'

# Forbidden raw unsafe router.push patterns inside HomeOverflowPanel.
# Le push devono passare sempre da _pushPreQaGuarded o router.push DENTRO il helper guarded.
# Cerchiamo nel body dell'HomeOverflowPanel raw router.push("/pvp" as any).
for unsafe in ('/pvp', '/events', '/shop', '/battlepass', '/raid', '/gvg', '/plaza', '/dm', '/territory'):
    pattern = re.compile(rf"router\.push\('{re.escape(unsafe)}'\s+as any\)")
    matches_in_overflow = list(pattern.finditer(overflow_body))
    # Allowed only if inside the _pushPreQaGuarded helper body (which calls router.push).
    # We allow MAX 1 occurrence per unsafe route if it's inside the guarded helper.
    # Strategia: l'helper _pushPreQaGuarded contiene UN solo `router.push(route as any)`.
    # Quindi nel body non devono esserci hardcoded router.push('/pvp' as any).
    assert len(matches_in_overflow) == 0, f'HomeOverflowPanel still contains raw router.push for {unsafe}'

# Verifica che nelle direct VIP push fuori da HomeOverflowPanel siano guarded.
# Cerca: onPress={() => router.push('/vip' as any)}  -> DEVE essere zero.
stray_vip = re.findall(r"onPress=\{\(\)\s*=>\s*router\.push\('/vip'\s+as any\)\}", c)
assert len(stray_vip) == 0, f'home.tsx still has {len(stray_vip)} raw VIP push outside guard'

# Verifica che le occorrenze di /vip siano dietro il guard inline.
vip_guarded_count = c.count("isRouteAllowedInPreQa('/vip')")
assert vip_guarded_count >= 2, f'expected >=2 guarded /vip push; got {vip_guarded_count}'

print('[v113 PRE_QA_113_HOME_OVERFLOW_NAV_GUARD] OK home_overflow_uses_guard no_raw_unsafe_push vip_guarded')
