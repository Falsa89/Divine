#!/usr/bin/env python3
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src=open(os.path.join(R,'backend/routes/daily_quest_tracker.py')).read()
for needle in [
    'TRACKER_KILL_SWITCH_ENV = "DAILY_QUEST_TRACKER_ENABLED"',
    'TRACKER_COLLECTION = "daily_quest_progress"',
    'ux_user_server_quest_day_pack99',
    'pack_99_test_artifact',
    'DAILY_QUEST_TRACKER_DISABLED',
    'COMPLETION_ENDPOINT_TEST_ONLY',
    'PLAYER_SERVER_PROFILE_REQUIRED',
    'QUEST_ID_NOT_WHITELISTED',
    'no_reward_grant_on_completion',
    'is_quest_completed',
    'mark_quest_claimed',
    'partialFilterExpression',
    '_slc_pack_99_tracker',
    '/daily-quest/progress',
    '/daily-quest/progress/complete',
    '/daily-quest/tracker/health',
]:
    assert needle in src, needle
# Must NOT leak reward grant inside the tracker file
for forbidden in [
    'soft_currencies', 'mission_coins', 'honor', 'PSP grant',
    'reward_claim_ledger', 'gems', 'gold',
]:
    assert forbidden not in src, f'tracker leaked reward field: {forbidden}'
print('[v110 PACK_99_DAILY_QUEST_TRACKER_ENDPOINT] OK kill_switch_dedicated test_only_marker server_scoped unique_index no_reward_grant_in_tracker')
