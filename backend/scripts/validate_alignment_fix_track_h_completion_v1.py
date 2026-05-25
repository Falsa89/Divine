#!/usr/bin/env python3
# ALIGNMENT_FIX Track H — completion.
import json, sys, hashlib
from pathlib import Path
P = Path('/app/data/design/audit/alignment_fix/track_h_completion_v1.json')
BE = Path('/app/backend/battle_engine.py')
ENV = Path('/app/backend/.env')
ROOT = Path('/app')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_H_BACKEND_FRONTEND_ALIGNMENT_COMPLETION_READY'
    assert d['global_verdict'] == 'PROJECT_BACKEND_FRONTEND_ALIGNMENT_AND_DANGEROUS_SURFACES_FIX_COMPLETE'
    # MD5 invariants
    assert md5(BE) == d['invariant_files_md5']['battle_engine_py'], 'battle_engine drift'
    assert md5(ENV) == d['invariant_files_md5']['backend_env'], '.env drift'
    # files changed: solo soul-forge.tsx
    fc = d['file_changed']
    assert len(fc) == 1
    sf = fc[0]
    assert sf['file'] == 'frontend/app/soul-forge.tsx'
    actual = md5(ROOT / sf['file'])
    assert actual == sf['md5_post'], f'soul-forge drift: {actual}'
    # No prohibited mutations
    for k in ('db_writes', 'backend_changes', 'flag_flips', 'new_live_buttons',
              'runtime_mutations', 'forbidden_violations'):
        assert d[k] == 0, f'{k} should be 0'
    # All tracks READY/FIXED_SAFE
    for k in 'ABCDEFGH':
        v = d['track_verdicts'][k]
        assert 'READY' in v or 'FIXED_SAFE' in v, f'bad verdict track {k}: {v}'
    # Next batch sequence popolata
    assert len(d['next_batch_sequence']) >= 8
    # Progress sane
    dpp = d['progress_estimate']['delta_pp']
    assert 0 <= dpp <= 2.0
    print(f"[PASS] ALIGN-FIX Track H completion \u2014 next={d['next_batch_sequence'][0]}")
    return 0
if __name__ == '__main__': sys.exit(main())
