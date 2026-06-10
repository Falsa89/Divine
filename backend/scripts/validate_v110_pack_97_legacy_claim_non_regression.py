#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_97_daily_login_claim_frontend_unlock/v110_pack_97_legacy_claim_non_regression_v1.json')))
assert d['only_new_real_source_added'] == 'daily_login_claim'
for k in ('mail_reward_claim_live','achievements_claim_live','battlepass_claim_live','afk_claim_live','event_claim_live','shop_claim_live'):
    assert d[k] is False, k
for k in ('pack_95_story_strict_preserved','pack_95_shops_buy_quarantine_preserved','pack_94_equipment_strict_preserved','pack_93_wallet_spend_preserved'):
    assert d[k] is True, k
import sys; sys.path.insert(0, os.path.join(R, 'backend'))
from utils.reward_source_registry import REWARD_SOURCE_REGISTRY
live_sources = [k for k, v in REWARD_SOURCE_REGISTRY.items() if v.get('live')]
allowed = {'qa_controlled_soft_currency_claim', 'story_progress_marker_claim', 'daily_login_claim'}
assert set(live_sources) == allowed, f'unexpected live sources: {live_sources}'
print('[v110 PACK_97_LEGACY_CLAIM_NON_REGRESSION] OK only_daily_login_new_source mail_achievements_battlepass_event_afk_NOT_LIVE pack_91_95_preserved')
