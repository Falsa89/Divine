#!/usr/bin/env python3
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_kill_switch_and_flags_v1.json')))
assert d['all_kill_switches_default_off'] is True and d['and_logic_required'] is True
assert d['backend_daily_quest_kill_switch']['default'] is False
assert d['frontend_daily_home_unlock_flag']['default']=='false'
print('[v110 PACK_98_KILL_SWITCH_AND_FLAGS] OK all_default_off AND_logic frontend_default_off')
