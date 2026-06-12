#!/usr/bin/env python3
"""Pre-QA Stabilization 112 — ROLLUP."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUIRED = (
    'validate_pre_qa_stabilization_112_shared_nav_guard.py',
    'validate_pre_qa_stabilization_112_pre_battle_lobby_fix.py',
    'validate_pre_qa_stabilization_112_legacy_combat_quarantine.py',
    'validate_pre_qa_stabilization_112_heroes_gacha_dead_code.py',
    'smoke_pre_qa_stabilization_112_home_battle_entrypoint_cleanup.py',
)
for s in REQUIRED:
    assert os.path.exists(os.path.join(R, 'backend/scripts', s)), s
rep = os.path.join(R, 'docs/divine/114_PRE_QA_STABILIZATION_112_HOME_BATTLE_ENTRYPOINT_CLEANUP_FINAL_REPORT.md')
assert os.path.exists(rep)
print('[PRE_QA_STABILIZATION_112_ROLLUP] OK four_validators_smoke_present final_report_present')
