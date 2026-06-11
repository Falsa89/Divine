#!/usr/bin/env python3
"""Pack 102 — Cleanup/rollback script presence + safety."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'backend/scripts/cleanup_v110_pack_102_test_artifacts.py')
assert os.path.exists(p)
src=open(p).read()
for needle in [
    'pack_102_test_artifact','--apply','REFUSED BY DEFAULT',
    'TOWER_STRICT_PREFLIGHT_ENABLED',
    'player_server_profiles','tower_progress',
]:
    assert needle in src, needle
print('[v110 PACK_102_CLEANUP_ROLLBACK] OK refuse_by_default apply_required pack_102_marker_only')
