#!/usr/bin/env python3
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
assert not os.path.exists(os.path.join(R, 'backend/routes/event.py')), 'event.py legacy must NOT exist live'
assert not os.path.exists(os.path.join(R, 'backend/routes/events.py')) or open(os.path.join(R, 'backend/routes/events.py')).read().find('reward_claim_ledger.insert_one') == -1, 'event live reward route must not exist'
src = open(os.path.join(R, 'backend/routes/competitive_guards.py')).read()
assert 'NO_LIVE_EVENT_ROUTE_PRESENT' in src
assert 'event_reward_live_grant' in src
print('[v110 PACK_107_EVENT_AUDIT] OK no_live_event_route safe_by_absence preflight_present')
