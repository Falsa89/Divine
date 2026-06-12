#!/usr/bin/env python3
"""Pack 109 — Daily/DailyQuest/Controlled rewards RC audit (static)."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for rel, must_contain in (
    ('backend/routes/daily_login_claim.py', ['/daily-login/claim/health', 'DAILY_LOGIN_CLAIM_ENABLED', 'server_id']),
    ('backend/routes/daily_quest_claim.py', ['/daily-quest/claim/health', 'server_id']),
    ('backend/routes/daily_quest_tracker.py', ['/daily-quest/tracker/health', 'server_id']),
    ('backend/routes/controlled_rewards.py', ['/controlled-rewards/health', 'pack_106_test_artifact', 'server_id']),
):
    p = os.path.join(__import__('os').path.join(R, rel))
    c = open(p).read()
    for tok in must_contain:
        assert tok in c, f'{rel}: missing {tok}'
print('[v110 PACK_109_DAILY_DAILYQUEST_CONTROLLED_REWARDS_RC] OK four_routes_canonical_invariants_intact')
