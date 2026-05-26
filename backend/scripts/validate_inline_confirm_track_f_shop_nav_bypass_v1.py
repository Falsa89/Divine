#!/usr/bin/env python3
# INLINE_CONFIRM Track F — shop nav + bypass regression guard.
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/soul_forge/inline_confirm_track_f_shop_nav_bypass_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
SHOP = Path('/app/frontend/app/shop.tsx')
ITEM = Path('/app/frontend/app/item-shop.tsx')
EC = Path('/app/frontend/app/economy.tsx')
EX = Path('/app/frontend/app/exclusive.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_F_SHOP_NAV_AND_BYPASS_REGRESSION_GUARD_READY'
    t = F.read_text()
    # Soul forge nav buttons preserved
    for label in ('Apri Tesoreria', 'Vai al Negozio', 'Apri Negozio Oggetti'):
        assert label in t, f'soul forge nav button {label} missing'
    # Locked flags intact
    assert 'SHOP_LOCKED_V2 = true' in SHOP.read_text()
    assert 'ITEM_SHOP_LOCKED_V2 = true' in ITEM.read_text()
    # Economy / Exclusive untouched
    by_file = {c['file']: c for c in d['checks'] if 'md5' in c}
    assert md5(EC) == by_file['frontend/app/economy.tsx']['md5'], 'economy drift'
    assert md5(EX) == by_file['frontend/app/exclusive.tsx']['md5'], 'exclusive drift'
    et = EC.read_text()
    xt = EX.read_text()
    for bad in ("apiCall('/api/shops/buy'", "apiCall('/api/soul-forge/retire'", "apiCall('/api/exclusive/craft'"):
        assert bad not in et
        assert bad not in xt
    print('[PASS] INLINE_CONFIRM Track F shop nav + bypass regression guard')
    return 0
if __name__ == '__main__': sys.exit(main())
