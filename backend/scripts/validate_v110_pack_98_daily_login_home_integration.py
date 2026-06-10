#!/usr/bin/env python3
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_daily_login_home_integration_v1.json')))
assert d['hidden_in_production_default'] is True
assert d['server_scope_required_for_render'] is True
section=open(os.path.join(R,'frontend/src/components/DailyHomeRewardSection.tsx')).read()
assert 'DailyLoginClaimButton' in section and 'DailyQuestClaimButton' in section
for banned in ['MailRewardClaim','AchievementsRewardClaim','BattlepassRewardClaim','EventRewardClaim','AFKRewardClaim']:
    assert banned not in section, banned
print('[v110 PACK_98_DAILY_LOGIN_HOME_INTEGRATION] OK home_section_renders_daily_login_and_quest no_other_consumers')
