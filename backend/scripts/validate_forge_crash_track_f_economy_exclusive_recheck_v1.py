#!/usr/bin/env python3
# FORGE_CRASH Track F — economy/exclusive bypass recheck.
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/soul_forge/forge_crash_track_f_economy_exclusive_recheck_v1.json')
EC = Path('/app/frontend/app/economy.tsx')
EX = Path('/app/frontend/app/exclusive.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_F_ECONOMY_EXCLUSIVE_NAVIGATION_RECHECK_READY'
    by_file = {row['file']: row for row in d['recheck']}
    assert md5(EC) == by_file['frontend/app/economy.tsx']['md5'], 'economy drift'
    assert md5(EX) == by_file['frontend/app/exclusive.tsx']['md5'], 'exclusive drift'
    et = EC.read_text()
    xt = EX.read_text()
    assert "router.replace('/soul-forge')" in et
    assert 'Schermata legacy archiviata' in xt
    # No mutation routes called from these screens
    for forbidden in ("apiCall('/api/shops/buy'", "apiCall('/api/soul-forge/retire'",
                      "apiCall('/api/exclusive/craft'"):
        assert forbidden not in et, f'forbidden call in economy: {forbidden}'
        assert forbidden not in xt, f'forbidden call in exclusive: {forbidden}'
    print('[PASS] FORGE_CRASH Track F economy/exclusive recheck')
    return 0
if __name__ == '__main__': sys.exit(main())
