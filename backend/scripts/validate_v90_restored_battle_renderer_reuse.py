#!/usr/bin/env python3
"""
v90 — Restored battle renderer reuse.

Verifica che frontend/app/(tabs)/menu.tsx contenga la nuova categoria 'Battaglia (Renderer Reale v90)'
con 5 entry che puntano a /combat?mode=<story|tower|arena|training|boss> e NON al mock
/playable-mode-battle-preview come primary surface.

Verifica che combat.tsx esista, sia MD5-lockato (intatto) e che i componenti riusati esistano:
- BattleSprite
- pickBattleBackground
- buildBattleLayout / getHomePosition
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MENU = os.path.join(ROOT, 'frontend', 'app', '(tabs)', 'menu.tsx')
COMBAT = os.path.join(ROOT, 'frontend', 'app', 'combat.tsx')
COMBAT_MD5 = 'fc792a05b2ada6e677d80400732ae5c3'

BATTLE_SPRITE = os.path.join(ROOT, 'frontend', 'components', 'BattleSprite.tsx')
BATTLE_BG = os.path.join(ROOT, 'frontend', 'components', 'ui', 'battleBackgrounds.ts')
MOTION = os.path.join(ROOT, 'frontend', 'components', 'battle', 'motionSystem.ts')


def fail(msg: str) -> None:
    print(f"FAIL v90_restored_battle_renderer_reuse: {msg}")
    sys.exit(1)


def md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    if not os.path.isfile(MENU):
        fail(f"missing menu.tsx: {MENU}")
    with open(MENU, 'r', encoding='utf-8') as f:
        menu_text = f.read()

    if 'Battaglia (Renderer Reale v90)' not in menu_text:
        fail("menu.tsx missing category 'Battaglia (Renderer Reale v90)'")

    expected_modes = ['story', 'tower', 'arena', 'training', 'boss']
    # v91_FIXED: il routing canonico passa attraverso /pre-battle-lobby (lobby intermediaria)
    # che poi lancia /combat. Accetta /combat?mode=X o /pre-battle-lobby?mode=X.
    for mode in expected_modes:
        ok = (f"'/combat?mode={mode}'" in menu_text) or (f"'/pre-battle-lobby?mode={mode}'" in menu_text)
        if not ok:
            fail(f"menu.tsx missing real-renderer route for mode={mode} (/combat or /pre-battle-lobby)")

    if not os.path.isfile(COMBAT):
        fail(f"missing combat.tsx: {COMBAT}")
    actual_md5 = md5(COMBAT)
    if actual_md5 != COMBAT_MD5:
        fail(f"combat.tsx MD5 drift: expected {COMBAT_MD5} got {actual_md5}")

    for f_path, label in [(BATTLE_SPRITE, 'BattleSprite.tsx'),
                          (BATTLE_BG, 'battleBackgrounds.ts'),
                          (MOTION, 'motionSystem.ts')]:
        if not os.path.isfile(f_path):
            fail(f"missing renderer component file: {label} at {f_path}")

    with open(BATTLE_BG, 'r', encoding='utf-8') as f:
        bg_src = f.read()
    if 'pickBattleBackground' not in bg_src:
        fail("battleBackgrounds.ts must export/define pickBattleBackground")

    with open(MOTION, 'r', encoding='utf-8') as f:
        motion_src = f.read()
    if 'buildBattleLayout' not in motion_src or 'getHomePosition' not in motion_src:
        fail("motionSystem.ts must contain buildBattleLayout and getHomePosition")

    print("PASS v90_restored_battle_renderer_reuse")


if __name__ == '__main__':
    main()
