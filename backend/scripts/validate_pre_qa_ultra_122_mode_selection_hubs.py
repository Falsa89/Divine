#!/usr/bin/env python3
"""Pack 122 — validate_pre_qa_ultra_122_mode_selection_hubs.

Verifica che le 5 mode (story/tower/training/arena/boss) abbiano hub/selection
files esistenti e che le 2 nuove preview hub esistano.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(HERE))

REQUIRED_HUBS = [
    ('story',    'frontend/app/story.tsx'),
    ('tower',    'frontend/app/tower-of-the-hells.tsx'),
    ('training', 'frontend/app/hero-training.tsx'),
    ('arena',    'frontend/app/arena-preview.tsx'),
    ('boss',     'frontend/app/boss-raid-preview.tsx'),
]


def main() -> int:
    failures = []
    for mode, fp in REQUIRED_HUBS:
        full = os.path.join(R, fp)
        if not os.path.exists(full):
            failures.append(f'hub mancante per mode {mode!r}: {fp}')
    # arena-preview e boss-raid-preview devono contenere router.push verso lobby
    for fp_rel in ('frontend/app/arena-preview.tsx',
                   'frontend/app/boss-raid-preview.tsx'):
        full = os.path.join(R, fp_rel)
        if os.path.exists(full):
            src = open(full, encoding='utf-8').read()
            if '/pre-battle-lobby?mode=' not in src:
                failures.append(f'{fp_rel} non porta a /pre-battle-lobby?mode=')
            for forbidden in ('reward', 'claim', 'grant', 'mmr'):
                # Permettiamo nel banner copy le parole "ricompensa"; ma proibiamo
                # 'reward'/'claim'/'grant'/'mmr' come token API.
                if f'{forbidden}(' in src.lower():
                    failures.append(f'{fp_rel} contiene chiamata {forbidden}()')
    if failures:
        print('[v122_mode_selection_hubs] FAIL')
        for f in failures:
            print(f'  - {f}')
        return 1
    print('[v122_mode_selection_hubs] OK 5_hubs_present arena_and_boss_preview_route_to_lobby no_reward_calls')
    return 0


if __name__ == '__main__':
    sys.exit(main())
