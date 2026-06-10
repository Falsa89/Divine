#!/usr/bin/env python3
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_live_readiness_update_v1.json')))
assert d['daily_login_home_ready'] is True
assert d['daily_login_home_unlocked_default'] is False
assert d['daily_quest_completion_claim_ready_status']=='READY_GATED_COMPLETION_REQUIRED'
for k in ('reward_live_general','premium_grants','mail_claim_live','achievements_claim_live','battlepass_claim_live','afk_claim_live','event_claim_live','shop_claim_live','release_readiness_claimed'):
    assert d[k] is False, k
assert d['second_real_player_facing_source_added']=='daily_quest_completion_claim'
assert d['only_two_real_player_facing_sources_total'] is True
print('[v110 PACK_98_LIVE_READINESS_UPDATE] OK home_ready_default_off quest_ready_gated 2_real_sources_total no_release_claim')
