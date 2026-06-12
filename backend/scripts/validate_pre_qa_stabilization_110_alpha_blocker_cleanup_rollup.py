#!/usr/bin/env python3
"""Pre-QA Stabilization 110 — ROLLUP."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUIRED = (
    'validate_pre_qa_stabilization_110_gacha_quarantine.py',
    'validate_pre_qa_stabilization_110_team_formation_quarantine.py',
    'validate_pre_qa_stabilization_110_use_server_scope_alias.py',
    'validate_pre_qa_stabilization_110_auth_token_bridge.py',
    'validate_pre_qa_stabilization_110_menu_cleanup.py',
    'validate_pre_qa_stabilization_110_achievements_quarantine.py',
    'validate_pre_qa_stabilization_110_mutating_route_allowlist.py',
    'validate_pre_qa_stabilization_110_static_anti_leak_guard.py',
    'validate_pre_qa_stabilization_110_data_invariants.py',
    'validate_pre_qa_stabilization_110_pack_91_109_qa_kickoff_preservation.py',
    'validate_pre_qa_stabilization_110_runtime_smoke_e2e.py',
    'validate_pre_qa_stabilization_110_final_report.py',
    'smoke_pre_qa_stabilization_110_alpha_blocker_cleanup.py',
)
for s in REQUIRED:
    assert os.path.exists(os.path.join(R, 'backend/scripts', s)), s
rep = os.path.join(R, 'docs/divine/112_PRE_QA_STABILIZATION_110_ALPHA_BLOCKER_CLEANUP_FINAL_REPORT.md')
assert os.path.exists(rep)
print('[PRE_QA_STABILIZATION_110_ROLLUP] OK twelve_validators_smoke_present final_report_present')
