#!/usr/bin/env python3
"""Pack 99 data invariants: nessun reward live general, nessun premium, nessuna mutazione vietata."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
claim=open(os.path.join(R,'backend/routes/daily_quest_claim.py')).read()
tracker=open(os.path.join(R,'backend/routes/daily_quest_tracker.py')).read()
# Claim must explicitly mark reward_live_general=False on response
assert '"reward_live_general": False' in claim, 'claim reward_live_general must be False'
# Tracker must explicitly mark reward_live_general False on health/responses
assert '"reward_live_general": False' in tracker, 'tracker reward_live_general must be False'
# Tracker must mark release_readiness_claimed False
assert '"release_readiness_claimed": False' in tracker, 'tracker release_readiness_claimed must be False'
# No premium fields in claim
for forbidden in ['users.gold', 'users.gems']:
    assert forbidden not in claim, f'premium leak: {forbidden}'
print('[v110 PACK_99_DATA_INVARIANTS] OK no_reward_live_general no_premium release_readiness_false')
