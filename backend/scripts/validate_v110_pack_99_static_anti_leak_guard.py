#!/usr/bin/env python3
"""Pack 99 anti-leak guard: il claim NON può grant senza tracker e nessuna scrittura premium e` consentita."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
claim=open(os.path.join(R,'backend/routes/daily_quest_claim.py')).read()
tracker=open(os.path.join(R,'backend/routes/daily_quest_tracker.py')).read()
# Anti-leak: must NOT have ANY of these patterns active in default path
for forbidden in [
    'users.gold', 'users.gems',
    'server_id="s1"', "server_id='s1'",
    'reward_live_general = true', 'reward_live_general=True',
    'release_readiness_claimed = True', 'release_readiness_claimed=True',
]:
    assert forbidden not in claim, f'leak in claim: {forbidden}'
    assert forbidden not in tracker, f'leak in tracker: {forbidden}'
# Tracker must NOT compute or apply rewards
for forbidden in ['grant_fn', 'reward_claim_ledger', 'mission_coins', 'honor']:
    assert forbidden not in tracker, f'tracker should not handle rewards: {forbidden}'
# Claim must consult tracker on default branch
assert 'await _tracker_is_completed(db, uid, sid, qid, day_override)' in claim
# Tracker complete endpoint must require marker pack_99_test_artifact
assert 'COMPLETION_ENDPOINT_TEST_ONLY' in tracker
assert 'pack_99_test_artifact' in tracker
print('[v110 PACK_99_STATIC_ANTI_LEAK_GUARD] OK no_premium_leak no_s1_hardcoded tracker_no_reward_grant claim_consults_tracker test_only_marker_enforced')
