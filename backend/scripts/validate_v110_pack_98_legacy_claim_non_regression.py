#!/usr/bin/env python3
import os, json, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_legacy_claim_non_regression_v1.json')))
assert d['only_two_real_player_facing_sources']==['daily_login_claim','daily_quest_completion_claim']
for k in ('mail_reward_claim_live','achievements_claim_live','battlepass_claim_live','afk_claim_live','event_claim_live','shop_claim_live'):
    assert d[k] is False, k
sys.path.insert(0,os.path.join(R,'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY
live=[k for k,v in REWARD_SOURCE_REGISTRY.items() if v.get('live')]
allowed={'qa_controlled_soft_currency_claim','story_progress_marker_claim','daily_login_claim','daily_quest_completion_claim'}
assert set(live)==allowed
print('[v110 PACK_98_LEGACY_CLAIM_NON_REGRESSION] OK 4_live_sources_total mail_achievements_etc_NOT_LIVE pack_91_97_preserved')
