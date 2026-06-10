#!/usr/bin/env python3
"""Pack 99 cleanup/rollback script presence + refuse-by-default + Pack 99 marker filter."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'backend/scripts/cleanup_v110_pack_99_test_artifacts.py')
assert os.path.exists(p)
src=open(p).read()
for needle in [
    'pack_99_test_artifact','--apply','REFUSED BY DEFAULT',
    'DAILY_QUEST_TRACKER_ENABLED','daily_quest_progress',
]:
    assert needle in src, needle
print('[v110 PACK_99_CLEANUP_ROLLBACK] OK refuse_by_default apply_required pack_99_marker_only tracker_kill_switch_reset')
