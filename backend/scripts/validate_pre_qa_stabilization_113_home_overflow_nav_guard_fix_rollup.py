#!/usr/bin/env python3
"""Pre-QA Stabilization 113 — ROLLUP."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUIRED = (
    'validate_pre_qa_stabilization_113_home_overflow_guard.py',
    'smoke_pre_qa_stabilization_113_home_overflow_nav_guard.py',
)
for s in REQUIRED:
    assert os.path.exists(os.path.join(R, 'backend/scripts', s)), s
rep = os.path.join(R, 'docs/divine/115_PRE_QA_STABILIZATION_113_HOME_OVERFLOW_NAV_GUARD_FIX_FINAL_REPORT.md')
assert os.path.exists(rep)
print('[PRE_QA_STABILIZATION_113_ROLLUP] OK validator_smoke_report_present')
