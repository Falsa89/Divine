#!/usr/bin/env python3
# PROJECT_SOUL_FORGE_EMERGENCY_RESTORE Track G — economy/exclusive bypass guards intact.
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/soul_forge/emergency_restore_track_g_bypass_guards_v1.json')
EC = Path('/app/frontend/app/economy.tsx')
EX = Path('/app/frontend/app/exclusive.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_G_ECONOMY_EXCLUSIVE_BYPASS_GUARDS_READY'
    # MD5 match
    by_file = {row['file']: row for row in d['checks']}
    assert md5(EC) == by_file['frontend/app/economy.tsx']['md5'], 'economy.tsx drift'
    assert md5(EX) == by_file['frontend/app/exclusive.tsx']['md5'], 'exclusive.tsx drift'
    et = EC.read_text()
    xt = EX.read_text()
    # economy: redirect-only, no mutation calls
    assert "router.replace('/soul-forge')" in et, 'economy redirect missing'
    for bad in ("apiCall('/api/shops/buy'", "apiCall('/api/soul-forge/retire'"):
        assert bad not in et, f'forbidden call in economy: {bad}'
    # exclusive: legacy lock notice, no craft mutation
    assert 'Schermata legacy archiviata' in xt, 'exclusive legacy lock notice missing'
    for bad in ("apiCall('/api/exclusive/craft'", "apiCall('/api/equipment/forge'"):
        assert bad not in xt, f'forbidden craft call in exclusive: {bad}'
    print('[PASS] EMERGENCY_RESTORE Track G economy/exclusive bypass guards intact')
    return 0
if __name__ == '__main__': sys.exit(main())
