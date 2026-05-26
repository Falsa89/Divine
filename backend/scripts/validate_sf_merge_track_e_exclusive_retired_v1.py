#!/usr/bin/env python3
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/audit/sf_merge/track_e_exclusive_retired_v1.json')
F = Path('/app/frontend/app/exclusive.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_E_EXCLUSIVE_ROUTE_RETIRED_LEGACY_LOCK_SAFE'
    assert d['strategy'] == 'legacy_lock_notice_with_redirect_options'
    assert d['character_bible_mutation'] is False
    assert md5(F) == d['exclusive_tsx_md5_post']
    t = F.read_text()
    for tok in ['legacy archiviata', 'character-bound', 'Divine Weapons',
                '/divine-weapons-catalog', '/soul-forge']:
        assert tok in t, f'missing token in exclusive.tsx: {tok}'
    forbidden = ['apiCall(', '/api/exclusive', "method: 'POST'"]
    for f in forbidden:
        assert f not in t, f'forbidden token in exclusive.tsx: {f}'
    print('[PASS] SF-MERGE Track E exclusive retired')
    return 0
if __name__=='__main__': sys.exit(main())
