#!/usr/bin/env python3
# PROJECT_BATCH_1_V2 Track H completion validator.
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/audit/batch1_v2/track_h_completion_v1.json')
BE = Path('/app/backend/battle_engine.py')
ENV = Path('/app/backend/.env')
ROOT = Path('/app')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_H_BATCH_1_V2_COMPLETION_AND_NEXT_PACKS_READY'
    assert d['global_verdict'] == 'PROJECT_BATCH_1_LOCK_DANGEROUS_PLAYER_SURFACES_V2_COMPLETE'
    # Invarianti MD5 backend
    assert md5(BE) == d['invariant_files_md5']['battle_engine_py'], 'battle_engine.py drift'
    assert md5(ENV) == d['invariant_files_md5']['backend_env'], '.env drift'
    # 8 file frontend modificati + md5 match
    fc = d['frontend_files_changed']
    assert len(fc) == 8, f'expected 8 frontend files, got {len(fc)}'
    for entry in fc:
        p = ROOT / entry['file']
        actual = md5(p)
        assert actual == entry['md5_post'], f'drift on {entry["file"]}: {actual} vs {entry["md5_post"]}'
    # Zero vincoli violati
    for k in ('db_writes', 'backend_changes', 'flag_flips', 'hero_deletion',
              'user_heroes_mutation', 'rate_changes', 'price_changes', 'reward_changes'):
        assert d[k] == 0, f'{k} should be 0'
    assert d['iap_implementation'] is False
    # Tutti gli 8 track verdetti READY/IMPLEMENTED_SAFE
    for k in 'ABCDEFGH':
        v = d['track_verdicts'][k]
        assert ('READY' in v) or ('IMPLEMENTED_SAFE' in v) or ('LOCKED_TO_PREVIEW_SAFE' in v), f'bad verdict track {k}: {v}'
    assert len(d['recommended_next_pack_order']) >= 6
    print(f"[PASS] BATCH1-V2 Track H completion \u2014 next={d['recommended_next_pack_order'][0]}")
    return 0
if __name__ == '__main__': sys.exit(main())
