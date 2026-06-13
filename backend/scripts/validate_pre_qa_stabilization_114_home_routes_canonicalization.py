#!/usr/bin/env python3
"""Pre-QA Stabilization 114 — Home routes canonicalization + dead-link guard.

Validator robusto (Pack 115A repair):
- non assume regex fragili con bracket annidati;
- estrae il body di `onHeroTap` tramite bracket matching;
- preserva tutti i check originali e aggiunge i check 115A richiesti dal pack:
  * zero `router.push('/profile' as any)` diretti SENZA guard nel file home;
  * `/research` bloccato in PRE_QA_BLOCKED_PLAYER_ROUTES;
  * HomeOverflow continua a usare `_pushPreQaGuarded`.

Output PASS singola riga, exit 0; in caso di fail solleva AssertionError.
"""
import os
import re

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
guard_fp = os.path.join(R, 'frontend/src/utils/preQaNavGuard.ts')
guard = open(guard_fp).read()
home = open(os.path.join(R, 'frontend/app/(tabs)/home.tsx')).read()
manifest = open(os.path.join(R, 'frontend/constants/homeAssetsManifest.ts')).read()


def _extract_arrow_body(src: str, start_marker: str) -> str:
    """Estrai il corpo `{...}` di una arrow function dato il marker iniziale.

    Esempio: start_marker='const onHeroTap = () => {'
    Ritorna la stringa che inizia dal `{` di apertura fino al `}` bilanciato.
    """
    idx = src.find(start_marker)
    assert idx >= 0, f'marker non trovato: {start_marker!r}'
    brace_open = src.find('{', idx)
    assert brace_open >= 0, 'no { dopo marker'
    depth = 0
    i = brace_open
    while i < len(src):
        c = src[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return src[brace_open:i + 1]
        i += 1
    raise AssertionError('body non chiuso (bracket non bilanciati)')


# 1) preQaNavGuard normalizza /(tabs)/x -> /x.
assert 'normalizeRoute' in guard
assert 'export function normalizeRoute' in guard
assert '\\([^)]+\\)' in guard or '/\\(' in guard, 'normalizeRoute regex per /(group)/x missing'
assert 'isRouteAllowedInPreQa' in guard

# 2) isRouteAllowedInPreQa usa normalize.
isr_body = _extract_arrow_body(guard, 'export function isRouteAllowedInPreQa')
assert 'normalizeRoute' in isr_body, 'isRouteAllowedInPreQa must call normalizeRoute'

# 3) /(tabs)/gacha viene normalizzato a /gacha che e' in blocked set.
assert "'/gacha'" in guard

# 4) Home hero tap /sanctuary guarded (estrazione robusta bracket-matched).
hero_body = _extract_arrow_body(home, 'const onHeroTap')
assert 'isRouteAllowedInPreQa' in hero_body, 'onHeroTap deve usare isRouteAllowedInPreQa'
assert "'/sanctuary'" in hero_body, 'onHeroTap deve riferirsi a /sanctuary'
assert 'PRE_QA_ROUTE_BLOCKED_LEGACY_OR_DEFERRED' in hero_body, 'onHeroTap deve dichiarare il blocker token'

# 5) Missing home routes /quests, /arena, /blessings, /profile, /research blocked.
for missing in ("'/quests'", "'/arena'", "'/blessings'", "'/profile'", "'/research'"):
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

# 9) Pack 115A — zero `router.push('/profile' as any)` diretti SENZA guard.
#    Un push diretto e' considerato "senza guard" se nella riga onPress che lo
#    contiene NON c'e' anche `isRouteAllowedInPreQa('/profile')`.
unguarded = []
for m in re.finditer(r"router\.push\(\s*['\"]/profile['\"]\s+as\s+any\s*\)", home):
    # finestra di 200 char prima della occorrenza per trovare il guard inline
    start = max(0, m.start() - 250)
    window = home[start:m.end()]
    if "isRouteAllowedInPreQa('/profile')" not in window:
        unguarded.append(m.start())
assert not unguarded, (
    f"Pack 115A: trovati {len(unguarded)} push diretti a /profile senza guard "
    f"(offsets: {unguarded[:5]}). Tutti i push devono essere preceduti da "
    f"isRouteAllowedInPreQa('/profile')."
)

# 10) Pack 115A — `/research` non deve essere usato in `_pushPreQaGuarded`
#    raw senza essere in PRE_QA_BLOCKED_PLAYER_ROUTES (gia' coperto dal check 5).
#    Inoltre research.tsx non deve esistere.
research_screen = os.path.join(R, 'frontend/app/research.tsx')
assert not os.path.exists(research_screen), (
    'frontend/app/research.tsx esiste — Pack 115A vieta la creazione della schermata research.'
)

# 11) Pack 115A — profile.tsx non deve esistere.
profile_screen = os.path.join(R, 'frontend/app/profile.tsx')
assert not os.path.exists(profile_screen), (
    'frontend/app/profile.tsx esiste — Pack 115A vieta la creazione della schermata profile.'
)

print('[v114 PRE_QA_114_HOME_ROUTES_CANONICALIZATION] OK normalizeRoute_present sanctuary_guarded missing_routes_blocked pack_113_preserved profile_guarded_115a research_blocked_115a no_dead_screens')
