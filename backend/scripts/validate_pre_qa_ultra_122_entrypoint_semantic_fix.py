#!/usr/bin/env python3
"""Pack 122 — validate_pre_qa_ultra_122_entrypoint_semantic_fix.

Fallisce se il menu pubblico contiene direct lobby entries player-facing
per i 5 mode (story/tower/arena/training/boss).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))
MENU = os.path.join(R, 'frontend', 'app', '(tabs)', 'menu.tsx')

FORBIDDEN_DIRECT_LOBBY = [
    '/pre-battle-lobby?mode=story',
    '/pre-battle-lobby?mode=tower',
    '/pre-battle-lobby?mode=arena',
    '/pre-battle-lobby?mode=training',
    '/pre-battle-lobby?mode=boss',
]


def main() -> int:
    if not os.path.exists(MENU):
        print('[v122_entrypoint_semantic] FAIL menu.tsx mancante')
        return 1
    src = open(MENU, encoding='utf-8').read()
    failures = []
    for route in FORBIDDEN_DIRECT_LOBBY:
        # Cerca solo le route literal nei campi route: '...'
        if re.search(rf"route:\s*'{re.escape(route)}'", src):
            failures.append(f'direct lobby entry player-facing presente: {route}')
    # Verifica che le 2 nuove preview hub siano presenti
    required_new_routes = ['/arena-preview', '/boss-raid-preview']
    for r in required_new_routes:
        if r not in src:
            failures.append(f'nuova preview hub mancante in menu: {r}')
    if failures:
        print('[v122_entrypoint_semantic] FAIL')
        for f in failures:
            print(f'  - {f}')
        return 1
    print('[v122_entrypoint_semantic] OK 5_modes_via_hubs no_direct_lobby_in_menu arena_and_boss_preview_present')
    return 0


if __name__ == '__main__':
    sys.exit(main())
