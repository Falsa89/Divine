#!/usr/bin/env python3
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/audit/sf_merge/track_h_completion_v1.json')
BE = Path('/app/backend/battle_engine.py')
ENV = Path('/app/backend/.env')
ROOT = Path('/app')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_H_SOUL_FORGE_ECONOMY_MERGE_AND_EXCLUSIVE_RETIREMENT_COMPLETION_READY'
    assert d['global_verdict'] == 'PROJECT_SOUL_FORGE_ECONOMY_MERGE_AND_EXCLUSIVE_RETIREMENT_COMPLETE'
    # Invarianti backend
    assert md5(BE) == d['invariant_files_md5']['battle_engine_py']
    assert md5(ENV) == d['invariant_files_md5']['backend_env']
    # 5 files changed + md5 match
    fc = d['files_changed']
    assert len(fc) == 5
    for entry in fc:
        p = ROOT / entry['file']
        actual = md5(p)
        assert actual == entry['md5_post'], f'drift on {entry["file"]}: {actual}'
    # Forbidden scope
    for k in ('db_writes','backend_changes','flag_flips','hero_deletion',
              'user_heroes_mutation','rate_changes','price_changes','reward_changes'):
        assert d[k] == 0
    assert d['iap_implementation'] is False
    assert d['character_bible_mutation'] is False
    # All tracks READY/SAFE/FIXED_SAFE
    for k in 'ABCDEFGH':
        v = d['track_verdicts'][k]
        assert 'READY' in v or 'SAFE' in v
    assert len(d['recommended_next_pack_order']) >= 6
    print(f"[PASS] SF-MERGE Track H completion \u2014 next={d['recommended_next_pack_order'][0]}")
    return 0
if __name__=='__main__': sys.exit(main())
