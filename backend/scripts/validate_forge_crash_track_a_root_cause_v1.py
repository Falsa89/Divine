#!/usr/bin/env python3
# FORGE_CRASH Track A — root cause documented.
import json, sys
from pathlib import Path
J = Path('/app/data/design/soul_forge/forge_crash_root_cause_v1.json')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_A_SOUL_FORGE_FORGE_CRASH_ROOT_CAUSE_IDENTIFIED'
    # Backend contract audit must conclude correct
    bca = d['backend_contract_audit']
    assert bca['endpoint'] == 'POST /api/soul/forge'
    assert bca['response_shape'] == {'gained_essence': 'int', 'new_balance': 'int'}
    assert 'BACKEND CONTRACT IS CORRECT' in bca['conclusion']
    # Must list at least 4 crash candidates
    assert len(d['frontend_crash_candidates']) >= 4
    ids = {c['id'] for c in d['frontend_crash_candidates']}
    assert 'FC1_SET_BALANCE_UNDEFINED' in ids
    assert 'FC2_RESULT_NEW_BALANCE_RENDER' in ids
    assert 'no_validator_weakening' in d['forbidden_kept_clean']
    print('[PASS] FORGE_CRASH Track A root cause documented')
    return 0
if __name__ == '__main__': sys.exit(main())
