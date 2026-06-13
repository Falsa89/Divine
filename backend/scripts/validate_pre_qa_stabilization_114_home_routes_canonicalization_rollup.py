#!/usr/bin/env python3
"""Pre-QA Stabilization 114 — ROLLUP."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUIRED = (
    'validate_pre_qa_stabilization_114_home_routes_canonicalization.py',
    'smoke_pre_qa_stabilization_114_home_routes_canonicalization.py',
)
for s in REQUIRED:
    assert os.path.exists(os.path.join(R, 'backend/scripts', s)), s
assert os.path.exists(os.path.join(R, 'docs/divine/116_PRE_QA_STABILIZATION_114_HOME_ROUTES_CANONICALIZATION_FINAL_REPORT.md'))
print('[PRE_QA_STABILIZATION_114_ROLLUP] OK validator_smoke_report_present')
