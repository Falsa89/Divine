#!/usr/bin/env python3
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_frontend_daily_quest_guard_v1.json')))
assert d['feature_flag_default']=='false'
assert d['visible_in_production_by_default'] is False
assert d['no_mail_achievements_battlepass_event_afk_consumers'] is True
btn=open(os.path.join(R,'frontend/src/components/DailyQuestClaimButton.tsx')).read()
for st in ['idle','loading','claimed','already_claimed','completion_required','kill_switch_off','whitelist_error','psp_missing','error']:
    assert st in btn, st
assert 'EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED' in btn
for banned in ['mail_reward','achievements_claim','battlepass_claim','event_claim','afk_claim']:
    assert banned not in btn, banned
print('[v110 PACK_98_FRONTEND_DAILY_QUEST_GUARD] OK feature_flag_default_off all_states no_other_consumers')
