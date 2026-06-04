#!/usr/bin/env python3
"""
v91_FIXED — Pre-battle lobby flow validator.

Verifica:
- frontend/app/pre-battle-lobby.tsx esiste
- contiene SourceBadge (source canonica visibile)
- contiene il bottone Modifica Team -> /(tabs)/battle (formation editor)
- contiene il bottone Avvia Battaglia -> /combat?mode=...&encounter_id=...
- NESSUN Math.random / random / Random per enemy selection
- random_opponents_allowed=false dichiarato nel codice
- (tabs)/menu.tsx routa le 5 modalita' alla pre-battle-lobby (NON direttamente a /combat)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOBBY = os.path.join(ROOT, 'frontend', 'app', 'pre-battle-lobby.tsx')
MENU = os.path.join(ROOT, 'frontend', 'app', '(tabs)', 'menu.tsx')


def fail(msg: str) -> None:
    print(f"FAIL v91_pre_battle_lobby_flow: {msg}")
    sys.exit(1)


def main() -> None:
    if not os.path.isfile(LOBBY):
        fail(f"missing pre-battle-lobby.tsx: {LOBBY}")
    with open(LOBBY, 'r', encoding='utf-8') as f:
        lobby = f.read()

    for token in ('SourceBadge', 'Modifica Team', 'Avvia Battaglia',
                  'random_opponents_allowed=false', 'is_random: false',
                  'runtime_generated: false', 'fallback_random_allowed: false'):
        if token not in lobby:
            fail(f"lobby missing required token: {token}")

    # Modifica Team must navigate to formation editor
    if "router.push('/(tabs)/battle'" not in lobby:
        fail("Modifica Team must navigate to /(tabs)/battle (formation editor)")

    # Avvia Battaglia must build /combat path with encounter_id
    if "`/combat?mode=" not in lobby or 'encounter_id=' not in lobby:
        fail("Avvia Battaglia must build /combat?mode=X&encounter_id=Y")

    # No runtime random for enemy selection
    forbidden = [r'\bMath\.random\s*\(', r'\brandom\(', r'\bRandom\(']
    for pat in forbidden:
        if re.search(pat, lobby):
            fail(f"lobby contains forbidden runtime random pattern: {pat}")

    if not os.path.isfile(MENU):
        fail(f"missing menu.tsx: {MENU}")
    with open(MENU, 'r', encoding='utf-8') as f:
        menu = f.read()

    # Le 5 entry della categoria reale devono puntare alla lobby (non direttamente a /combat)
    real_cat = 'Battaglia (Renderer Reale v90)'
    idx = menu.find(real_cat)
    if idx < 0:
        fail("menu.tsx missing real category title 'Battaglia (Renderer Reale v90)'")
    end_marker = 'Wireframe Deprecato v90'
    end_idx = menu.find(end_marker, idx)
    if end_idx < 0:
        fail("menu.tsx missing deprecated marker after real category")
    block = menu[idx:end_idx]

    lobby_modes = re.findall(r"route:\s*'/pre-battle-lobby\?mode=([a-z]+)'", block)
    if sorted(lobby_modes) != sorted(['story', 'tower', 'arena', 'training', 'boss']):
        fail(f"menu.tsx real category must route to /pre-battle-lobby for 5 modes; got {lobby_modes}")

    print("PASS v91_pre_battle_lobby_flow")


if __name__ == '__main__':
    main()
