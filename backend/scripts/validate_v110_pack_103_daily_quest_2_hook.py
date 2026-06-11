#!/usr/bin/env python3
"""Pack 103 - Daily quest event mapping tower_floor_clear_success -> daily_quest_2."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src=open(os.path.join(R,'backend/utils/daily_quest_events.py')).read()
assert '"tower_floor_clear_success": "daily_quest_2"' in src
assert '"tower_floor_clear_success": {"tower_strict_battle_execute"}' in src
print('[v110 PACK_103_DAILY_QUEST_2_HOOK] OK event_mapping_added source_route_allowlisted')
