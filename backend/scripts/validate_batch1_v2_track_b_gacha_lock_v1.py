#!/usr/bin/env python3
# PROJECT_BATCH_1_V2 Track B validator (gacha lock).
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/audit/batch1_v2/track_b_gacha_lock_v1.json')
F = Path('/app/frontend/app/(tabs)/gacha.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_B_GACHA_PLAYER_SURFACE_LOCK_OR_GUARD_IMPLEMENTED_SAFE'
    assert d['rate_changes'] == 0
    assert d['pity_changes'] == 0
    assert d['pool_changes'] == 0
    assert d['backend_changes'] == 0
    assert d['db_writes'] == 0
    assert set(d['locked_banners_v2']) == {'premium', 'targeted'}
    assert set(d['hidden_banners_v2']) == {'artifact', 'constellation'}
    # File content checks
    text = F.read_text()
    assert 'LOCKED_BANNERS_V2' in text and 'HIDDEN_BANNERS_V2' in text
    assert 'isActiveBannerLocked' in text
    assert 'IN REVISIONE' in text
    # MD5 match
    assert md5(F) == d['gacha_tsx_md5_post'], f'gacha drift: {md5(F)}'
    print('[PASS] BATCH1-V2 Track B gacha lock')
    return 0
if __name__ == '__main__': sys.exit(main())
