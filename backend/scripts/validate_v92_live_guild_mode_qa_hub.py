#!/usr/bin/env python3
"""v92 — Live/Guild Mode QA Hub mobile screen validator.

Verifica:
- frontend/app/live-guild-qa-hub.tsx esiste
- contiene tutte le label QA richieste
- contiene tutte le 10 mode card live/guild/special
- NO Math.random / random
- (tabs)/menu.tsx contiene la categoria 'Modalita\' Live & Guild QA (v92)'
- frontend/app/live-mode-pre-entry-lobby.tsx esiste e routa a /combat
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HUB = os.path.join(ROOT, 'frontend', 'app', 'live-guild-qa-hub.tsx')
LOBBY = os.path.join(ROOT, 'frontend', 'app', 'live-mode-pre-entry-lobby.tsx')
MENU = os.path.join(ROOT, 'frontend', 'app', '(tabs)', 'menu.tsx')

REQUIRED_TOKENS_HUB = [
    'TEST', 'QA',
    'NO LIVE REWARD', 'NO RANKING APPLIED', 'NO CURRENCY', 'NO SCORE MUT',
    'random_opponents_allowed=false',
    'production_enabled=false', 'qa_override_only=true',
]
REQUIRED_MODE_IDS_HUB = {
    'event', 'crepuscolo_dei_titani', 'assalto_del_ragnarok',
    'guild_war', 'guild_raid', 'server_boss', 'faction_boss',
    'territory', 'war_avatar_mode', 'event_avatar_mode',
}
REQUIRED_TOKENS_LOBBY = [
    'qa_override_only', 'production_enabled', 'reward_live',
    'NO LIVE REWARD', 'NO RANKING APPLIED', 'NO GUILD SCORE',
    'is_random: false', 'runtime_generated: false',
]


def fail(msg): print(f"FAIL v92_live_guild_mode_qa_hub: {msg}"); sys.exit(1)


def main():
    if not os.path.isfile(HUB): fail(f"missing hub: {HUB}")
    if not os.path.isfile(LOBBY): fail(f"missing live pre-entry lobby: {LOBBY}")
    if not os.path.isfile(MENU): fail(f"missing menu.tsx: {MENU}")

    with open(HUB, 'r', encoding='utf-8') as f: hub = f.read()
    for t in REQUIRED_TOKENS_HUB:
        if t not in hub: fail(f"hub missing token: {t}")
    for mid in REQUIRED_MODE_IDS_HUB:
        if f"'{mid}'" not in hub:
            fail(f"hub missing mode_id: {mid}")
    for pat in [r'\bMath\.random\s*\(', r'\brandom\(']:
        if re.search(pat, hub):
            fail(f"hub contains forbidden random pattern: {pat}")

    with open(LOBBY, 'r', encoding='utf-8') as f: lobby = f.read()
    for t in REQUIRED_TOKENS_LOBBY:
        if t not in lobby: fail(f"lobby missing token: {t}")
    if '/combat?mode=' not in lobby:
        fail("lobby must route to /combat?mode= for battle modes")
    for pat in [r'\bMath\.random\s*\(', r'\brandom\(']:
        if re.search(pat, lobby):
            fail(f"lobby contains forbidden random pattern: {pat}")

    with open(MENU, 'r', encoding='utf-8') as f: menu = f.read()
    if "Modalit\u00e0 Live & Guild QA (v92)" not in menu and 'Modalit\u00e0 Live & Guild QA' not in menu:
        fail("menu.tsx missing 'Modalita\u0301 Live & Guild QA (v92)' category")
    if "'/live-guild-qa-hub'" not in menu:
        fail("menu.tsx missing route to /live-guild-qa-hub")

    print("PASS v92_live_guild_mode_qa_hub")


if __name__ == '__main__': main()
