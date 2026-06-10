#!/usr/bin/env python3
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data/design/v110_pack_99_daily_quest_runtime_tracker_home_unlock/v110_pack_99_daily_quest_tracker_sot_v1.json')))
assert d['tracker_id']=='daily_quest_completion_runtime_tracker'
assert d['storage']['collection_name']=='daily_quest_progress'
assert d['storage']['key_fields']==['user_id','server_id','quest_id','day_iso']
assert d['quest_id_whitelist']==['daily_quest_1','daily_quest_2','daily_quest_3']
assert d['completion_source']=='server_side_only'
assert d['tracker_kill_switch_env']=='DAILY_QUEST_TRACKER_ENABLED'
assert d['tracker_kill_switch_default'] is False
assert d['daily_quest_claim_enforced_on_completion'] is True
assert d['client_cannot_set_state_freely'] is True
assert d['no_reward_grant_on_completion'] is True
assert d['reward_live_general'] is False
assert d['release_readiness_claimed'] is False
assert d['approval_received']=='AUTORIZZO_V110_DAILY_QUEST_RUNTIME_TRACKER_AND_HOME_UNLOCK_PACK_99'
sot=os.path.join(R,'docs/divine/119_DAILY_QUEST_RUNTIME_TRACKER_SOT.md')
assert os.path.exists(sot)
print('[v110 PACK_99_DAILY_QUEST_RUNTIME_TRACKER_SOT] OK collection=daily_quest_progress whitelist_3 server_side_only kill_switch_default_off no_reward_on_completion')
