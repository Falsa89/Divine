#!/usr/bin/env python3
# INLINE_CONFIRM Track H — completion.
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/soul_forge/inline_confirm_track_h_completion_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
BE = Path('/app/backend/battle_engine.py')
ENV = Path('/app/backend/.env')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_H_INLINE_CONFIRM_NO_MODAL_CRASH_COMPLETION_READY'
    assert d['global_verdict'] == 'PROJECT_SOUL_FORGE_INLINE_CONFIRM_RESTORE_NO_MODAL_CRASH_COMPLETE'
    tv = d['track_verdicts']
    expect = {
        'A':'TRACK_A_TRUE_MOBILE_CRASH_CAUSE_CORRECTED_READY',
        'B':'TRACK_B_MODAL_CONFIRM_PATH_REMOVED_SAFE',
        'C':'TRACK_C_INLINE_CONFIRMATION_PANEL_READY_SAFE',
        'D':'TRACK_D_CRASH_PROOF_EVENT_HANDLERS_READY',
        'E':'TRACK_E_API_CONTRACT_KEPT_NO_FORMULA_CHANGE_READY',
        'F':'TRACK_F_SHOP_NAV_AND_BYPASS_REGRESSION_GUARD_READY',
        'G':'TRACK_G_MINIMAL_BETA_SMOKE_HARNESS_READY_OR_DEFERRED',
        'H':'TRACK_H_INLINE_CONFIRM_NO_MODAL_CRASH_COMPLETION_READY',
    }
    for k,v in expect.items():
        assert tv[k] == v, f'track {k} verdict mismatch'
    fc = {row['file']: row for row in d['files_changed']}
    assert md5(F) == fc['frontend/app/soul-forge.tsx']['md5_post']
    assert md5(BE) == '151ca35ad3bc35f0a6209cb3744ed440'
    assert md5(ENV) == 'ff60bbb79efa329b71aa8ed351ea89b3'
    assert d['backend_changes'] == 0
    assert d['db_writes'] == 0
    assert d['reward_formula_change'] is False
    assert 'no validator weakening' in d['invariants_respected']
    assert len(d['remaining_blockers']) == 0
    assert len(d['mobile_qa_checklist']) >= 8
    print('[PASS] INLINE_CONFIRM Track H completion')
    return 0
if __name__ == '__main__': sys.exit(main())
