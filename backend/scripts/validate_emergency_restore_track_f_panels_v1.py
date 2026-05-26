#!/usr/bin/env python3
# PROJECT_SOUL_FORGE_EMERGENCY_RESTORE Track F — panels (materials/shop/treasury/rules).
import json, sys
from pathlib import Path
J = Path('/app/data/design/soul_forge/emergency_restore_track_f_panels_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_F_SOUL_FORGE_MATERIALS_SHOP_TREASURY_PANELS_READY'
    t = F.read_text()
    # ANIME HUB panels presence
    assert 'ANIME HUB' in t, 'ANIME HUB section missing'
    assert 'Materiali Anime' in t, 'Materiali Anime card missing'
    assert 'Valute Globali' in t, 'Tesoreria currencies card missing'
    assert 'Negozio Anime' in t, 'Shop preview missing'
    assert 'Negozio Polvere Stellare' in t, 'star dust shop preview missing'
    assert 'Regole / Protezioni' in t, 'rules card missing'
    # Read-only locks present, no buy button rendered
    assert 'READ-ONLY' in t, 'READ-ONLY badge missing'
    assert 'COMPRA' not in t, 'Live buy button must NOT be rendered'
    # Treasury link
    assert "/treasury'" in t or '"/treasury"' in t, 'treasury route push missing'
    # Material fields shown
    for label in ('Soul Essence','Prana','Sigilli Anima','Polvere Stellare'):
        assert label in t, f'material label {label} missing'
    # Read-only fetches use safe endpoints only
    assert "apiCall('/api/wallet')" in t, 'wallet GET missing'
    assert "apiCall('/api/soul-forge')" in t, 'soul-forge GET missing'
    assert "apiCall('/api/shops')" in t, 'shops GET missing'
    # NO mutation endpoints other than /api/soul/forge
    assert '/api/shops/buy' not in t, 'shops buy mutation must NOT be present'
    assert '/api/soul-forge/retire' not in t, 'legacy retire mutation must NOT be present'
    print('[PASS] EMERGENCY_RESTORE Track F panels ready')
    return 0
if __name__ == '__main__': sys.exit(main())
