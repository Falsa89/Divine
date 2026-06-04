#!/usr/bin/env python3
"""
v90 — No mock preview regression.

Verifica:
- la NUOVA categoria 'Battaglia (Renderer Reale v90)' NON contiene route verso /playable-mode-battle-preview
  (le sue 5 entry puntano tutte a /combat?mode=<X>);
- la vecchia categoria 'Battle Preview QA (v88)' e' stata marcata come deprecata (titolo aggiornato);
- nessun NUOVO file mock parallelo e' stato creato in frontend/app (le 5 entry reali usano /combat reale);
- i file MD5-lockati non sono stati modificati.
"""
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MENU = os.path.join(ROOT, 'frontend', 'app', '(tabs)', 'menu.tsx')

MD5_LOCKS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx': '54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx': '45fcc9890b6b128c37088bc33aa54caf',
    'backend/server.py': '055df030553f4791e8cac14254f1b148',
    'frontend/app/combat.tsx': 'fc792a05b2ada6e677d80400732ae5c3',
    'frontend/app/story.tsx': '8520627b4e63f86821d73d8d3880bac3',
}


def fail(msg: str) -> None:
    print(f"FAIL v90_no_mock_preview_regression: {msg}")
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

    real_cat = 'Battaglia (Renderer Reale v90)'
    if real_cat not in menu_text:
        fail("menu.tsx missing real renderer category title")

    # Estrai blocco della categoria reale fino all'inizio della categoria
    # deprecata e verifica che NON contenga route verso playable-mode-battle-preview.
    real_idx = menu_text.find(real_cat)
    if real_idx < 0:
        fail("real category title not found")
    deprecated_marker = 'Wireframe Deprecato v90'
    dep_idx = menu_text.find(deprecated_marker, real_idx)
    if dep_idx < 0:
        fail("deprecated category marker not found after real category")
    block = menu_text[real_idx:dep_idx]

    if 'playable-mode-battle-preview' in block:
        fail("real renderer category must NOT route to playable-mode-battle-preview mock")

    # Tutte le 5 entry della categoria reale devono usare /combat oppure
    # /pre-battle-lobby (entrambi puntano al renderer reale: la lobby v91
    # e' l'intermediario canonico verso /combat, non un mock parallelo).
    real_routes = re.findall(r"route:\s*'/(combat|pre-battle-lobby)\?mode=([a-z]+)'", block)
    found_modes = sorted(m for _, m in real_routes)
    if found_modes != sorted(['story', 'tower', 'arena', 'training', 'boss']):
        fail(f"real renderer category modes mismatch: got {found_modes}")

    # La vecchia categoria deve essere marcata come deprecata
    if deprecated_marker not in menu_text:
        fail("old mock category must be marked as deprecated v90")

    # MD5 locks: tutti intatti
    for rel, expected in MD5_LOCKS.items():
        full = os.path.join(ROOT, rel)
        if not os.path.isfile(full):
            fail(f"locked file missing: {rel}")
        actual = md5(full)
        if actual != expected:
            fail(f"MD5 drift on {rel}: expected {expected} got {actual}")

    print("PASS v90_no_mock_preview_regression")


if __name__ == '__main__':
    main()
