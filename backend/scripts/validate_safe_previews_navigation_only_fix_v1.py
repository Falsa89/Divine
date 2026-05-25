#!/usr/bin/env python3
# PROJECT_PLAYER_FACING_LEGACY_SURFACES — Track B validator.
# Verifica che il fix navigation-only di safe-previews.tsx sia in place:
#  - design json presente e coerente;
#  - file frontend contiene chiamata router.push verso /status-codex,
#    /artifacts-preview, /housing-preview;
#  - non sono state introdotte chiamate apiCall/fetch live nel file;
#  - md5 post combacia.
import json, sys, hashlib, re
from pathlib import Path

D = Path('/app/data/design/frontend/project_safe_previews_navigation_only_fix_v1.json')
F = Path('/app/frontend/app/safe-previews.tsx')


def md5_of(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def main() -> int:
    d = json.loads(D.read_text())
    assert d['verdict'] == 'TRACK_B_SAFE_PREVIEWS_NAVIGATION_ONLY_FIX_IMPLEMENTED_SAFE'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['navigation_only'] is True
    assert d['new_live_buttons'] == 0
    assert d['new_api_calls'] == 0
    assert d['flag_flips'] == 0
    actual = md5_of(F)
    assert actual == d['safe_previews_tsx_md5_post'], f'safe-previews drift: {actual} vs {d["safe_previews_tsx_md5_post"]}'
    text = F.read_text()
    # destinazioni attese
    for route in ('/status-codex', '/artifacts-preview', '/housing-preview'):
        assert route in text, f'route {route} missing in safe-previews.tsx'
    # router.push presente
    assert 'router.push' in text, 'router.push not found'
    # nessuna nuova chiamata mutativa
    forbidden = ['apiCall(', 'fetch(', '/api/shop/buy', '/api/artifacts/pull', '/api/battlepass/']
    for tok in forbidden:
        assert tok not in text, f'forbidden token {tok} present in safe-previews.tsx'
    # onPress direttamente su SafeFeatureCard (no wrapper Touchable esterno)
    assert re.search(r'SafeFeatureCard[^>]*onPress=', text, re.DOTALL), 'SafeFeatureCard must receive onPress directly'
    print('[PASS] PLAYER-LEGACY Track B safe-previews navigation-only fix in place')
    return 0


if __name__ == '__main__':
    sys.exit(main())
