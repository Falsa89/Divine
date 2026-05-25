#!/usr/bin/env python3
# PROJECT_MODE_WIRING_REGISTRY / TRACK H + GLOBAL COMPLETION
import json, sys, hashlib
from pathlib import Path

P = Path('/app/data/design/project_management/project_mode_wiring_registry_completion_v1.json')
REG = Path('/app/data/design/frontend/mode_feature_wiring_registry_v1.json')
BE = Path('/app/backend/battle_engine.py')
ENV = Path('/app/backend/.env')

def md5_of(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()

def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_H_PROJECT_MODE_WIRING_COMPLETION_READY'
    assert d['global_verdict'] == 'PROJECT_MODE_WIRING_REGISTRY_AND_LEGACY_ROUTE_AUDIT_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['frontend_changes'] == 0
    assert d['flag_flips'] == 0
    # MD5 invariants
    expected_be = '151ca35ad3bc35f0a6209cb3744ed440'
    expected_env = 'ff60bbb79efa329b71aa8ed351ea89b3'
    assert d['battle_engine_md5_pre'] == expected_be
    assert d['battle_engine_md5_post'] == expected_be
    assert d['env_md5_pre'] == expected_env
    assert d['env_md5_post'] == expected_env
    # Reality check
    assert md5_of(BE) == expected_be, f'battle_engine MD5 drift! {md5_of(BE)}'
    assert md5_of(ENV) == expected_env, f'.env MD5 drift! {md5_of(ENV)}'
    # Registry present
    assert REG.exists()
    reg = json.loads(REG.read_text())
    assert reg['verdict'] == 'PROJECT_MODE_WIRING_REGISTRY_AND_LEGACY_ROUTE_AUDIT_READY'
    assert reg['summary_counts']['total_modes_registered'] >= 25
    # Track verdicts present
    tv = d['track_verdicts']
    for k in 'ABCDEFGH':
        assert k in tv and 'READY' in tv[k]
    # Recommended next pack present
    assert d['recommended_next_pack_primary']
    # readiness improved
    assert d['frontend_integration_readiness_post'] >= d['frontend_integration_readiness_pre']
    # progress unchanged or +0.001 max
    diff = d['progress_estimate']['global_project_post'] - d['progress_estimate']['global_project_pre']
    assert abs(diff) <= 0.01, f'progress drifted: {diff}'
    print(f"[PASS] Track H mode wiring completion READY \u2014 fe_readiness={d['frontend_integration_readiness_post']}%, mode_wiring_readiness={d['mode_wiring_readiness_estimate']}%, next={d['recommended_next_pack_primary']}")
    return 0
if __name__ == '__main__': sys.exit(main())
