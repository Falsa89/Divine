#!/usr/bin/env python3
"""Pack 109 — Arena/PvP/Event guards RC audit."""
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
c = open(os.path.join(R, 'backend/routes/competitive_guards.py')).read()
for tok in ('arena/preflight', 'pvp/preflight', 'event/preflight', 'guild/preflight',
            'ARENA_REWARD_LIVE_DISABLED', 'PVP_RANKING_SERVER_SCOPE_DEFERRED',
            'EVENT_REWARD_LIVE_DISABLED', 'GUILD_REWARD_LIVE_DISABLED',
            'READY_GATED_REWARDS_DEFERRED', 'pack_107_test_artifact'):
    assert tok in c, f'competitive_guards missing {tok}'
print('[v110 PACK_109_ARENA_PVP_EVENT_RC] OK four_preflights_intact deferred_blockers_canonical')
