#!/usr/bin/env python3
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/audit/sf_merge/track_d_economy_retired_v1.json')
F = Path('/app/frontend/app/economy.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_D_ECONOMY_ROUTE_RETIRED_TO_SOUL_FORGE_SAFE'
    assert d['strategy'] == 'redirect_to_soul_forge'
    assert d['redirect_target'] == '/soul-forge'
    assert md5(F) == d['economy_tsx_md5_post']
    t = F.read_text()
    for tok in ["router.replace('/soul-forge')", "Economia trasferita"]:
        assert tok in t, f'missing token in economy.tsx: {tok}'
    forbidden = ['/api/economy/buy', '/api/economy/retire', 'apiCall(']
    for f in forbidden:
        assert f not in t, f'forbidden token in economy.tsx: {f}'
    print('[PASS] SF-MERGE Track D economy retired')
    return 0
if __name__=='__main__': sys.exit(main())
