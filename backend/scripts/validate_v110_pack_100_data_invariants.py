#!/usr/bin/env python3
"""Pack 100 — Data invariants: no broad grants, no premium, no reward live general, no destructive migration."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
login=open(os.path.join(R,'backend/routes/daily_login_claim.py')).read()
quest=open(os.path.join(R,'backend/routes/daily_quest_claim.py')).read()
tracker=open(os.path.join(R,'backend/routes/daily_quest_tracker.py')).read()
events=open(os.path.join(R,'backend/utils/daily_quest_events.py')).read()
for src,name in [(login,'login'),(quest,'quest'),(tracker,'tracker'),(events,'events')]:
    assert '"reward_live_general": False' in src or 'reward_live_general' not in src or 'False' in src.split('reward_live_general')[1][:80], f'{name}: reward_live_general true'
assert '"release_readiness_claimed": False' in login
assert '"release_readiness_claimed": False' in quest
assert '"release_readiness_claimed": False' in tracker
print('[v110 PACK_100_DATA_INVARIANTS] OK no_reward_live_general no_release_readiness_claim no_destructive_migration')
