#!/usr/bin/env python3
"""Pack 100 — Static server-scope anti-leak guard (active player-facing path)."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for f in [
    'backend/routes/daily_login_claim.py',
    'backend/routes/daily_quest_claim.py',
    'backend/routes/daily_quest_tracker.py',
    'backend/utils/daily_quest_events.py',
]:
    src=open(os.path.join(R,f)).read()
    # Active path NEVER allowed: hardcoded s1, gold/gems mutation, reward_live_general=True
    for forbidden in [
        'server_id="s1"', "server_id='s1'",
        'users.gold', 'users.gems',
        '"reward_live_general": True',
        'reward_live_general=True',
        '"release_readiness_claimed": True',
        'release_readiness_claimed=True',
    ]:
        assert forbidden not in src, f'{f}: leak {forbidden}'
    # SERVER_ID_REQUIRED enforcement (must be present in claim+tracker)
    if 'claim' in f or 'tracker' in f:
        assert 'SERVER_ID_REQUIRED' in src or 'PLAYER_SERVER_PROFILE_REQUIRED' in src, f'{f}: missing server_id guard'
print('[v110 PACK_100_STATIC_SERVER_SCOPE_ANTI_LEAK] OK no_hardcoded_s1 no_user_gold_gems_mutate no_reward_live_general server_id_required_enforced')
