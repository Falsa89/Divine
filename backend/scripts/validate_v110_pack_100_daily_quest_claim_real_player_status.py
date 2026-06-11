#!/usr/bin/env python3
"""Pack 100 — Daily Quest claim real-player status update (health snapshot map)."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src=open(os.path.join(R,'backend/routes/daily_quest_claim.py')).read()
assert 'pack_100_event_bridge_integrated' in src
assert 'pack_100_quest_real_completion_event_status' in src
for q,status in [
    ('daily_quest_1','REAL_COMPLETION_EVENT_READY'),
    ('daily_quest_2','COMPLETION_RUNTIME_DEFERRED'),
    ('daily_quest_3','COMPLETION_RUNTIME_DEFERRED'),
]:
    assert f'"{q}": "{status}"' in src, f'{q} status missing'
print('[v110 PACK_100_DAILY_QUEST_CLAIM_REAL_PLAYER_STATUS] OK quest_1_real_ready quest_2_3_deferred event_bridge_integrated')
