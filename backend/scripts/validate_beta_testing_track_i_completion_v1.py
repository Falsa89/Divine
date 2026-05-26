#!/usr/bin/env python3
# BETA_TESTING Track I — completion.
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/testing/beta_testing_track_i_completion_v1.json')
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_I_BETA_TESTING_AUTOMATION_REDIS_STABILIZATION_COMPLETION_READY'
    assert d['global_verdict'] == 'PROJECT_BETA_TESTING_AUTOMATION_HARNESS_AND_REDIS_STABILIZATION_COMPLETE'
    expect = {
        'A':'TRACK_A_BASELINE_AND_BRANCH_POLICY_LOCKED',
        'B':'TRACK_B_PLAYER_ROUTE_STATIC_AUDIT_SCRIPT_READY',
        'C':'TRACK_C_SOUL_FORGE_REGRESSION_STATIC_TESTS_READY',
        'D':'TRACK_D_LOCKED_SURFACES_STATIC_TESTS_READY',
        'E':'TRACK_E_PLAYWRIGHT_EXPO_WEB_SMOKE_HARNESS_READY',
        'F':'TRACK_F_REDIS_INFRA_STABILIZED',
        'G':'TRACK_G_BETA_REPORTING_AND_SCREENSHOT_ARTIFACTS_STANDARDIZED',
        'H':'TRACK_H_SUITE_REGISTRY_AND_VALIDATORS_READY',
        'I':'TRACK_I_BETA_TESTING_AUTOMATION_REDIS_STABILIZATION_COMPLETION_READY',
    }
    for k,v in expect.items():
        assert d['track_verdicts'][k] == v, f'track {k} verdict mismatch'
    # invariants intact
    assert md5('/app/backend/battle_engine.py') == '151ca35ad3bc35f0a6209cb3744ed440'
    assert md5('/app/backend/.env') == 'ff60bbb79efa329b71aa8ed351ea89b3'
    assert d['backend_changes'] == 0 and d['db_writes'] == 0
    assert d['reward_formula_change'] is False
    assert 'no validator weakening' in d['invariants_respected']
    assert d['redis_failing_count_after'] == 0
    assert d['player_route_audit_results']['fail'] == 0
    assert len(d['remaining_blockers']) == 0
    print('[PASS] BETA_TESTING Track I completion')
    return 0
if __name__ == '__main__': sys.exit(main())
