#!/usr/bin/env python3
# FORGE_CRASH Track H — completion.
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/soul_forge/forge_crash_track_h_completion_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
BE = Path('/app/backend/battle_engine.py')
ENV = Path('/app/backend/.env')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_H_SOUL_FORGE_FORGE_CRASH_API_CONTRACT_SHOP_NAV_COMPLETION_READY'
    assert d['global_verdict'] == 'PROJECT_SOUL_FORGE_FORGE_CRASH_API_CONTRACT_AND_SHOP_NAV_FIX_COMPLETE'
    tv = d['track_verdicts']
    expect = {
        'A': 'TRACK_A_SOUL_FORGE_FORGE_CRASH_ROOT_CAUSE_IDENTIFIED',
        'B': 'TRACK_B_FRONTEND_FORGE_CRASH_PROOFING_FIXED_SAFE',
        'C': 'TRACK_C_BACKEND_FORGE_ENDPOINT_CONTRACT_ALIGNED_OR_VERIFIED',
        'D': 'TRACK_D_MOBILE_CONFIRM_MODAL_AND_POST_SUCCESS_STATE_SAFE',
        'E': 'TRACK_E_SOUL_SHOP_NAVIGATION_BUTTONS_READY_SAFE',
        'F': 'TRACK_F_ECONOMY_EXCLUSIVE_NAVIGATION_RECHECK_READY',
        'G': 'TRACK_G_REDIS_SUITE_NOISE_AND_TEST_CREDENTIALS_HYGIENE_READY',
        'H': 'TRACK_H_SOUL_FORGE_FORGE_CRASH_API_CONTRACT_SHOP_NAV_COMPLETION_READY',
    }
    for k, v in expect.items():
        assert tv[k] == v, f'track {k} verdict mismatch'
    # MD5 checks for files_changed
    by_file = {row['file']: row for row in d['files_changed']}
    assert md5(F) == by_file['frontend/app/soul-forge.tsx']['md5_post']
    # Invariants intact
    assert md5(BE) == '151ca35ad3bc35f0a6209cb3744ed440', 'battle_engine drift'
    assert md5(ENV) == 'ff60bbb79efa329b71aa8ed351ea89b3', '.env drift'
    assert d['backend_changes'] == 0
    assert d['db_writes'] == 0
    assert d['reward_formula_change'] is False
    assert 'no validator weakening' in d['invariants_respected']
    assert 'no plaintext password committed' in d['invariants_respected']
    assert len(d['remaining_blockers']) == 0
    print('[PASS] FORGE_CRASH Track H completion')
    return 0
if __name__ == '__main__': sys.exit(main())
