#!/usr/bin/env python3
import os, json, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_reward_payload_guard_v1.json')))
assert d['fixed_reward_server_side']=={'mission_coins':15,'honor':8}
assert d['client_payload_ignored'] is True and d['amount_cap_per_key']==100
sys.path.insert(0,os.path.join(R,'backend'))
from utils.reward_source_registry import _grant_daily_quest_to_psp
out=_grant_daily_quest_to_psp(None,'uid','sid',{'gold':999999})  # payload ignored
assert out=={'soft_currencies.mission_coins':15,'soft_currencies.honor':8}, out
print('[v110 PACK_98_REWARD_PAYLOAD_GUARD] OK fixed_reward_server_side client_payload_ignored no_premium')
