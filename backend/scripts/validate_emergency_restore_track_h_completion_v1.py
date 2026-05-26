#!/usr/bin/env python3
# PROJECT_SOUL_FORGE_EMERGENCY_RESTORE Track H — completion.
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/soul_forge/emergency_restore_track_h_completion_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_H_SOUL_FORGE_EMERGENCY_RESTORE_AND_FULL_MERGE_COMPLETION_READY'
    assert d['global_verdict'] == 'PROJECT_SOUL_FORGE_EMERGENCY_RESTORE_AND_FULL_MERGE_FIX_COMPLETE'
    tv = d['track_verdicts']
    expect = {
        'A':'TRACK_A_SOUL_FORGE_BLANK_SCREEN_ROOT_CAUSE_IDENTIFIED',
        'B':'TRACK_B_SOUL_FORGE_VISIBLE_SCREEN_RESTORED_SAFE',
        'C':'TRACK_C_SOUL_FORGE_HERO_GRID_AND_FILTERS_RESTORED',
        'D':'TRACK_D_SOUL_FORGE_MOBILE_LAYOUT_AND_CONFIRM_MODAL_FIXED',
        'E':'TRACK_E_FULL_ECONOMY_LEGACY_CONTENT_IMPORT_AUDIT_READY',
        'F':'TRACK_F_SOUL_FORGE_MATERIALS_SHOP_TREASURY_PANELS_READY',
        'G':'TRACK_G_ECONOMY_EXCLUSIVE_BYPASS_GUARDS_READY',
        'H':'TRACK_H_SOUL_FORGE_EMERGENCY_RESTORE_AND_FULL_MERGE_COMPLETION_READY',
    }
    for k, v in expect.items():
        assert tv[k] == v, f'track {k} verdict mismatch'
    # Files changed match actual MD5s
    fc = {row['file']: row for row in d['files_changed']}
    assert md5(F) == fc['frontend/app/soul-forge.tsx']['md5_post']
    assert d['backend_changes'] == 0
    assert d['db_writes'] == 0
    assert 'backend/battle_engine.py untouched' in d['invariants_respected']
    assert 'no validator weakening' in d['invariants_respected']
    assert len(d['remaining_blockers']) == 0
    assert len(d['mobile_qa_checklist']) >= 8
    print('[PASS] EMERGENCY_RESTORE Track H completion ready')
    return 0
if __name__ == '__main__': sys.exit(main())
