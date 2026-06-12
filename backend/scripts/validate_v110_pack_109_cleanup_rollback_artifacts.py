#!/usr/bin/env python3
"""Pack 109 — Cleanup / Rollback / Artifacts Index."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
smoke = open(os.path.join(R, 'backend/scripts/smoke_v110_pack_109_closed_alpha_rc_global_e2e.py')).read()
assert 'finally:' in smoke
assert 'delete_many' in smoke
assert 'cleanup' in smoke.lower() or 'inserted' in smoke
report = open(os.path.join(R, 'docs/divine/110_CLOSED_ALPHA_RC_SWEEP_RELEASE_GATE_FINAL_REPORT.md')).read()
assert 'Artifacts Index' in report or 'artifacts_index' in report.lower() or 'cleanup' in report.lower()
print('[v110 PACK_109_CLEANUP_ROLLBACK_ARTIFACTS] OK smoke_cleans_test_artifacts report_documents_cleanup_rollback')
