#!/usr/bin/env python3
"""Pack 100 — Daily Quest claim real-player status update (rebased canonical post Pack 103).

CANONICAL BASELINE EVOLUTION:
  * Pack 100 baseline: daily_quest_1 REAL_COMPLETION_EVENT_READY, _2/_3 DEFERRED.
  * Pack 103 reconciled (approved): daily_quest_2 ora REAL via tower_floor_clear_success.
"""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src=open(os.path.join(R,'backend/routes/daily_quest_claim.py')).read()
assert 'pack_100_event_bridge_integrated' in src
assert 'pack_100_quest_real_completion_event_status' in src
# Pack 100 baseline (riga 1).
assert '"daily_quest_1": "REAL_COMPLETION_EVENT_READY"' in src, 'daily_quest_1 status missing'
# Pack 103 canonical (riga 2): daily_quest_2 ora REAL via tower clear.
assert ('"daily_quest_2": "REAL_COMPLETION_EVENT_READY_VIA_TOWER_CLEAR"' in src
        or '"daily_quest_2": "REAL_COMPLETION_EVENT_READY"' in src), \
    'daily_quest_2 must be REAL via tower clear (Pack 103 canonical)'
# daily_quest_3 ancora DEFERRED.
assert '"daily_quest_3": "COMPLETION_RUNTIME_DEFERRED"' in src, 'daily_quest_3 status missing'
print('[v110 PACK_100_DAILY_QUEST_CLAIM_REAL_PLAYER_STATUS] OK canonical_post_pack_103 quest_1_real_ready quest_2_real_via_tower_clear quest_3_deferred event_bridge_integrated')
