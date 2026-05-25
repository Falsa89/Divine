#!/usr/bin/env python3
# PROJECT_BATCH_1_V2 Track E validator (shop/bp/vip/item-shop lock).
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/audit/batch1_v2/track_e_shop_bp_vip_lock_v1.json')
ROOT = Path('/app')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_E_SHOP_BATTLEPASS_VIP_MONETIZATION_LOCK_IMPLEMENTED_SAFE'
    assert d['price_changes'] == 0
    assert d['item_changes'] == 0
    assert d['reward_changes'] == 0
    assert d['premium_logic_changes'] == 0
    assert d['iap_implementation'] is False
    assert d['backend_changes'] == 0
    assert d['db_writes'] == 0
    # Verifica MD5 dei file modificati + lock token presente
    for surf in d['surfaces_locked']:
        p = ROOT / surf['file']
        assert md5(p) == surf['md5_post'], f'drift on {surf["file"]}'
        text = p.read_text()
        assert '_LOCKED_V2' in text, f'lock flag missing in {surf["file"]}'
        assert 'lockBannerV2' in text or 'IN REVISIONE' in text, f'lock UI missing in {surf["file"]}'
    print('[PASS] BATCH1-V2 Track E shop/bp/vip/item-shop lock')
    return 0
if __name__ == '__main__': sys.exit(main())
