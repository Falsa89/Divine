#!/usr/bin/env python3
"""Pre-QA Stabilization 111 — ROLLUP."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUIRED = (
    'validate_pre_qa_stabilization_111_route_classification.py',
    'validate_pre_qa_stabilization_111_auth_token_compat_adoption.py',
    'validate_pre_qa_stabilization_111_validators_registered.py',
    'validate_pre_qa_stabilization_111_md5_rebaseline_authorized.py',
    'smoke_pre_qa_stabilization_111_rebaseline_route_classification.py',
)
for s in REQUIRED:
    assert os.path.exists(os.path.join(R, 'backend/scripts', s)), s
rep = os.path.join(R, 'docs/divine/113_PRE_QA_STABILIZATION_111_REBASELINE_ROUTE_CLASSIFICATION_FINAL_REPORT.md')
assert os.path.exists(rep)
print('[PRE_QA_STABILIZATION_111_ROLLUP] OK four_validators_smoke_present final_report_present')
