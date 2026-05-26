#!/usr/bin/env python3
# INLINE_CONFIRM Track G — minimal static smoke harness.
import json, sys
from pathlib import Path
J = Path('/app/data/design/soul_forge/inline_confirm_track_g_smoke_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
EC = Path('/app/frontend/app/economy.tsx')
EX = Path('/app/frontend/app/exclusive.tsx')
SHOP = Path('/app/frontend/app/shop.tsx')
ITEM = Path('/app/frontend/app/item-shop.tsx')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_G_MINIMAL_BETA_SMOKE_HARNESS_READY_OR_DEFERRED'
    t = F.read_text()
    # Smoke check 1: no <Modal> rendered
    assert '<Modal' not in t, 'Modal element still rendered in soul-forge'
    # Smoke check 2: no Modal import from react-native
    head = t.split("from 'react-native';")[0]
    assert 'Modal' not in head, 'Modal still in react-native import'
    assert 'KeyboardAvoidingView' not in head
    # Smoke check 3: inline confirm style is present
    assert 'inlineConfirmCard:' in t, 'inlineConfirmCard style missing'
    assert 'setInlineConfirmOpen(true)' in t and 'setInlineConfirmOpen(false)' in t
    # Smoke check 4: economy/exclusive locked
    assert "router.replace('/soul-forge')" in EC.read_text()
    assert 'Schermata legacy archiviata' in EX.read_text()
    # Smoke check 5: shop locked flags
    assert 'SHOP_LOCKED_V2 = true' in SHOP.read_text()
    assert 'ITEM_SHOP_LOCKED_V2 = true' in ITEM.read_text()
    # Smoke check 6: no live forbidden api calls in economy/exclusive
    for path in (EC, EX):
        ct = path.read_text()
        for forbidden in ("apiCall('/api/shops/buy'", "apiCall('/api/soul-forge/retire'",
                          "apiCall('/api/exclusive/craft'"):
            assert forbidden not in ct, f'forbidden call {forbidden} present in {path}'
    print('[PASS] INLINE_CONFIRM Track G minimal static smoke')
    return 0
if __name__ == '__main__': sys.exit(main())
