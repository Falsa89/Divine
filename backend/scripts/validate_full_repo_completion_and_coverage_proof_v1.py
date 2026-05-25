#!/usr/bin/env python3
# PROJECT_FULL_REPO_CONSISTENCY_AUDIT — Track H completion validator.
import json, sys, hashlib
from pathlib import Path
P = Path('/app/data/design/audit/full_repo/full_repo_audit_completion_coverage_v1.json')
BE = Path('/app/backend/battle_engine.py')
ENV = Path('/app/backend/.env')
REQUIRED_ARTIFACTS = [
    'frontend_route_menu_registry_v1.json',
    'frontend_api_callsite_registry_v1.json',
    'backend_endpoint_mutation_registry_v1.json',
    'feature_mode_crosswalk_v1.json',
    'economy_gacha_roster_risk_audit_v1.json',
    'gates_locked_preview_dev_surface_audit_v1.json',
    'master_fix_backlog_and_batching_plan_v1.json',
    'feature_completeness_gap_matrix_v1.json',
    'full_repo_audit_completion_coverage_v1.json',
]
BASE = Path('/app/data/design/audit/full_repo')

def md5_of(p):
    return hashlib.md5(p.read_bytes()).hexdigest()

def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_H_FULL_REPO_AUDIT_COMPLETION_AND_COVERAGE_PROOF_READY'
    assert d['global_verdict'] == 'PROJECT_FULL_REPO_CONSISTENCY_AUDIT_AND_MASTER_FIX_PLAN_READY'
    assert d['mode'] == 'audit_only_no_runtime_changes'
    # Invarianti MD5
    assert md5_of(BE) == d['invariant_files_md5']['battle_engine_py'], 'battle_engine.py drift'
    assert md5_of(ENV) == d['invariant_files_md5']['backend_env'], '.env drift'
    # Tutti i track verdict READY
    for k in 'ABCDEFGH':
        assert 'READY' in d['track_verdicts'][k]
    # Tutti gli artifact presenti
    for name in REQUIRED_ARTIFACTS:
        assert (BASE / name).exists(), f'missing artifact: {name}'
    # Coverage sane
    cov = d['scan_coverage']
    assert cov['frontend_routes_scanned'] >= 40
    assert cov['backend_endpoints_scanned'] >= 100
    assert cov['frontend_api_callsites_scanned'] >= 80
    assert cov['feature_gap_matrix_entries'] >= 30
    assert cov['master_backlog_entries'] >= 20
    # Zero mutations
    for k in ('db_writes', 'backend_changes', 'frontend_changes', 'flag_flips',
              'new_live_buttons', 'runtime_mutations'):
        assert d[k] == 0
    # Progress delta entro 2pp
    dpp = d['progress_estimate']['delta_pp']
    assert 0 <= dpp <= 2.0
    print(f"[PASS] FULL-REPO Track H \u2014 coverage routes={cov['frontend_routes_scanned']} endpoints={cov['backend_endpoints_scanned']} callsites={cov['frontend_api_callsites_scanned']} features={cov['feature_gap_matrix_entries']}")
    return 0
if __name__ == '__main__': sys.exit(main())
