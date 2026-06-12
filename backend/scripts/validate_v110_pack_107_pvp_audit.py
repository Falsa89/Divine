#!/usr/bin/env python3
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
assert not os.path.exists(os.path.join(R, 'backend/routes/pvp.py')), 'pvp.py legacy must NOT exist live'
src = open(os.path.join(R, 'backend/routes/competitive_guards.py')).read()
assert 'NO_LIVE_PVP_RANKING_ROUTE_PRESENT' in src
assert 'pvp_reward_live_grant' in src
print('[v110 PACK_107_PVP_AUDIT] OK no_live_pvp_route safe_by_absence preflight_present')
