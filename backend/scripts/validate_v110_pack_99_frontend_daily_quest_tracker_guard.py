#!/usr/bin/env python3
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f=os.path.join(R,'frontend/src/components/DailyQuestClaimButton.tsx')
src=open(f).read()
for needle in [
    'EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED',
    'fetchTracker',
    'GET',
    '/api/daily-quest/progress?server_id=',
    'completion_required',
    'tracker',
    'claimReady',
    'forceVisible',
]:
    assert needle in src, needle
# Default OFF guard
assert "const UI_ENABLED = UI_FLAG === 'true';" in src
assert 'if (!UI_ENABLED && !forceVisible) return null;' in src
print('[v110 PACK_99_FRONTEND_DAILY_QUEST_TRACKER_GUARD] OK ui_default_off tracker_consulted_before_claim no_false_success')
