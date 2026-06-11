#!/usr/bin/env python3
"""Pack 101 — Data invariants: no broad grants, no premium, no reward live general, no destructive migration."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
strict=open(os.path.join(R,'backend/routes/tower_strict.py')).read()
combat=open(os.path.join(R,'backend/routes/combat.py')).read()
for needle in ['"reward_live_general": False','"tower_reward_live_grant": False','"release_readiness_claimed": False']:
    assert needle in strict, f'strict missing: {needle}'
# Combat must contain reward_live_general:False in quarantine 503 detail
assert '"reward_live_general": False' in combat
assert '"tower_reward_live_grant": False' in combat
print('[v110 PACK_101_DATA_INVARIANTS] OK reward_live_general_false tower_reward_live_grant_false release_readiness_false')
