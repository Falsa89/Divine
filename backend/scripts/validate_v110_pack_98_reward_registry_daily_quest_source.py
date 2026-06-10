#!/usr/bin/env python3
import os, json, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_reward_registry_daily_quest_source_v1.json')))
assert d['new_source_id']=='daily_quest_completion_claim'
sd=d['source_definition']
assert sd['live'] is True and sd['per_source_kill_switch_default'] is False
assert sd['fixed_reward']=={'mission_coins':15,'honor':8}
assert sd['completion_proof_required'] is True
sys.path.insert(0,os.path.join(R,'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY, list_allowlisted_sources
assert 'daily_quest_completion_claim' in REWARD_SOURCE_REGISTRY
entry=REWARD_SOURCE_REGISTRY['daily_quest_completion_claim']
assert entry['fixed_reward']=={'mission_coins':15,'honor':8}
assert entry['per_source_kill_switch_env']=='DAILY_QUEST_CLAIM_ENABLED'
assert entry['completion_proof_required'] is True
assert entry['ready_status']=='READY_GATED_COMPLETION_REQUIRED'
live=set(list_allowlisted_sources())
assert {'qa_controlled_soft_currency_claim','story_progress_marker_claim','daily_login_claim','daily_quest_completion_claim'}<=live
print('[v110 PACK_98_REWARD_REGISTRY_DAILY_QUEST_SOURCE] OK quest_added pack96_97_sources_preserved fixed_reward_15_8')
