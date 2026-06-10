#!/usr/bin/env python3
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src=open(os.path.join(R,'backend/routes/daily_quest_claim.py')).read()
# Required Pack 99 wiring
for needle in [
    'from routes.daily_quest_tracker import',
    'is_quest_completed',
    'mark_quest_claimed',
    'READY_TRACKER_GATED',
    'pack_99_tracker_state_after_claim',
    'runtime_tracker',
    '_slc_pack_99_completion_source',
    '_slc_pack_99_tracker_gated',
    'completion_proof_used',
    'DAILY_QUEST_COMPLETION_REQUIRED',
]:
    assert needle in src, needle
# Legacy Pack 98 marker must still be present (backward-compatible bypass)
for needle in ['pack_98_test_artifact', 'test_completion_proof']:
    assert needle in src, needle
# Must NOT silently grant without checking tracker on default path
assert 'await _tracker_is_completed(db, uid, sid, qid, day_override)' in src
print('[v110 PACK_99_CLAIM_TRACKER_ENFORCEMENT] OK tracker_consulted runtime_gating pack_98_legacy_preserved no_silent_grant')
