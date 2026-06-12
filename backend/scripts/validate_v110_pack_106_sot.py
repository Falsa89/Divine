#!/usr/bin/env python3
"""Pack 106 — SOT (Source Of Truth) doc presence + canonical references."""
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sot = os.path.join(R, 'docs/divine/110_MAIL_ACHIEVEMENTS_DAILY_WEEKLY_CONTROLLED_REWARDS_SOT.md')
assert os.path.exists(sot), 'SOT doc missing'
src = open(sot).read()
for kw in ('mail_claim_controlled','achievement_claim_controlled','daily_weekly_reward_claim',
           'MAIL_CLAIM_CONTROLLED_ENABLED','ACHIEVEMENT_CLAIM_CONTROLLED_ENABLED','DAILY_WEEKLY_REWARD_CLAIM_ENABLED',
           'EXPO_PUBLIC_REWARD_CENTER_UI_ENABLED','EXPO_PUBLIC_MAIL_CLAIM_UI_ENABLED',
           'EXPO_PUBLIC_ACHIEVEMENT_CLAIM_UI_ENABLED','EXPO_PUBLIC_DAILY_WEEKLY_UI_ENABLED',
           'user_id + server_id','UTC_day','UTC_ISO_week',
           'reward_live_general=false','release_readiness_claimed=false',
           'users.gold','IAP','gacha',
           'ACHIEVEMENT_COMPLETION_REQUIRED','MAIL_REWARD_CATALOG_V1','ACHIEVEMENT_REWARD_CATALOG_V1',
           'DAILY_WEEKLY_REWARD_CATALOG_V1','no_battlepass_event_afk_pvp_guild_live'):
    assert kw in src, f'SOT missing: {kw}'
print('[v110 PACK_106_SOT] OK doc_present_all_canonical_keywords_present')
