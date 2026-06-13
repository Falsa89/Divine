#!/usr/bin/env python3
"""Pre-QA Stabilization 114 — Smoke (static).

Pack 115F repair:
- Rimossa regex fragile attorno a `onHeroTap` (rompeva su parentesi annidate
  introdotte da if/else interni al body).
- Lo smoke ora chiama esplicitamente il validator 114 (canonical) e fallisce
  se il validator fallisce.
- Sono preservati i check Pack 112/113 (chiamando i rispettivi validator).
- Sono mantenute le verifiche statiche aggiuntive che lo smoke faceva (shape
  generico di `normalizeRoute`, presenza set blocked, e — invece della regex
  fragile su `onHeroTap` — un check via bracket-matching robusto sull'arrow
  function, identico nella forma a quello usato dal validator 114).

Niente runtime, niente DB writes, niente attivazione feature.
"""
import os
import re
import subprocess
import sys

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS = os.path.join(R, 'backend', 'scripts')


def _extract_arrow_body(src: str, start_marker: str) -> str:
    """Estrai il corpo `{...}` di una arrow/function dato il marker iniziale.

    Bracket-matching robusto: non fa assunzioni sul contenuto del body.
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


# [1] Validator Pack 114 (canonical) — deve passare.
subprocess.check_call([sys.executable, os.path.join(SCRIPTS, 'validate_pre_qa_stabilization_114_home_routes_canonicalization.py')])
print('[1] validator Pack 114 PASS')

# [2] Pack 113 HomeOverflow guard ancora valido.
subprocess.check_call([sys.executable, os.path.join(SCRIPTS, 'validate_pre_qa_stabilization_113_home_overflow_guard.py')])
print('[2] Pack 113 HomeOverflow guard still PASS')

# [3] Pack 112 shared nav guard ancora valido.
subprocess.check_call([sys.executable, os.path.join(SCRIPTS, 'validate_pre_qa_stabilization_112_shared_nav_guard.py')])
print('[3] Pack 112 shared nav guard still PASS')

# [4] Sanity statica: la funzione normalizeRoute esiste e usa una regex per
#     gestire i gruppi /(group)/x. Non vincoliamo la forma esatta della regex
#     (per evitare regressioni se il validator ne accetta varianti), ma solo
#     che il blocco contenga il riferimento al match della parentesi di gruppo.
guard_fp = os.path.join(R, 'frontend/src/utils/preQaNavGuard.ts')
guard = open(guard_fp, 'r', encoding='utf-8').read()
norm_body = _extract_arrow_body(guard, 'export function normalizeRoute')
assert '\\(' in norm_body and '\\)' in norm_body, (
    'normalizeRoute deve contenere una regex che riconosce il gruppo /(group)/x'
)
print('[4] normalizeRoute regex shape OK (bracket-matched, non fragile)')

# [5] Tutte le missing routes critiche devono essere nel blocked set.
for needed in ("'/quests'", "'/arena'", "'/blessings'", "'/profile'", "'/gacha'", "'/sanctuary'"):
    assert needed in guard, f'shared guard missing block for {needed}'
print('[5] all blocked missing routes present in shared guard')

# [6] `onHeroTap` deve usare il guard. Estrazione bracket-matched, NON regex
#     fragile su `[^}]+\}\s*;` (che falliva se il body conteneva nested braces).
home_fp = os.path.join(R, 'frontend/app/(tabs)/home.tsx')
home = open(home_fp, 'r', encoding='utf-8').read()
hero_body = _extract_arrow_body(home, 'const onHeroTap')
assert 'isRouteAllowedInPreQa' in hero_body, (
    'onHeroTap deve usare isRouteAllowedInPreQa (guard obbligatorio).'
)
assert "'/sanctuary'" in hero_body, (
    "onHeroTap deve riferirsi a '/sanctuary' (la route target dell'hero).'"
)
print('[6] onHeroTap /sanctuary guarded OK (bracket-matched, non fragile)')

# [7] La tab gacha resta nascosta (Pack 110 invariant) — sanity.
layout = open(os.path.join(R, 'frontend/app/(tabs)/_layout.tsx'), 'r', encoding='utf-8').read()
assert 'href: null' in layout and 'EXPO_PUBLIC_GACHA_UI_ENABLED' in layout, (
    'Pack 110 invariant violato: tab gacha non piu nascosta dietro env flag.'
)
print('[7] gacha tab still hidden behind env flag OK')

print('SMOKE PRE_QA_STABILIZATION_114 OK')
