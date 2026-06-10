#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_97_daily_login_claim_frontend_unlock/v110_pack_97_reward_registry_daily_source_v1.json')))
assert d['new_source_id'] == 'daily_login_claim'
sd = d['source_definition']
assert sd['server_scoped'] is True and sd['live'] is True
assert sd['per_source_kill_switch_default'] is False
assert sd['fixed_reward'] == {'mission_coins': 10, 'honor': 5}
import sys; sys.path.insert(0, os.path.join(R, 'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY, list_allowlisted_sources
assert 'daily_login_claim' in REWARD_SOURCE_REGISTRY
entry = REWARD_SOURCE_REGISTRY['daily_login_claim']
assert entry['live'] is True
assert entry['fixed_reward'] == {'mission_coins': 10, 'honor': 5}
assert entry['per_source_kill_switch_env'] == 'DAILY_LOGIN_CLAIM_ENABLED'
assert 'qa_controlled_soft_currency_claim' in list_allowlisted_sources()
assert 'story_progress_marker_claim' in list_allowlisted_sources()
assert 'daily_login_claim' in list_allowlisted_sources()
print('[v110 PACK_97_REWARD_REGISTRY_DAILY_SOURCE] OK daily_added pack96_sources_preserved fixed_reward_10_5')
