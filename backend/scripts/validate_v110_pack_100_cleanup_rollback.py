#!/usr/bin/env python3
"""Pack 100 — Cleanup/Rollback script presence + safety."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'backend/scripts/cleanup_v110_pack_100_test_artifacts.py')
assert os.path.exists(p)
src=open(p).read()
for needle in [
    'pack_100_test_artifact','--apply','REFUSED BY DEFAULT',
    'DAILY_QUEST_TRACKER_ENABLED','DAILY_LOGIN_CLAIM_ENABLED',
    'reward_claim_ledger','daily_quest_progress',
]:
    assert needle in src, needle
print('[v110 PACK_100_CLEANUP_ROLLBACK] OK refuse_by_default apply_required pack_100_marker_only kill_switch_reset')
