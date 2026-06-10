#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_97_daily_login_claim_frontend_unlock/v110_pack_97_live_readiness_update_v1.json')))
for k in ('daily_login_claim_ready','only_one_new_player_facing_source_in_pack_97','reward_ledger_live_pack_96_preserved','frontend_daily_login_ui_added_gated','frontend_ui_default_hidden','wallet_spend_ledger_pack_93_preserved','equipment_strict_pack_94_preserved','story_strict_pack_95_preserved','legacy_quarantine_pack_94_95_preserved'):
    assert d[k] is True, k
for k in ('daily_login_claim_live_enabled_default','global_reward_kill_switch_default','reward_live_general','premium_grants','mail_claim_live','achievements_claim_live','battlepass_claim_live','afk_claim_live','event_claim_live','shop_claim_live','release_readiness_claimed'):
    assert d[k] is False, k
assert d['first_real_player_facing_source_added'] == 'daily_login_claim'
print('[v110 PACK_97_LIVE_READINESS_UPDATE] OK daily_login_ready_default_off only_one_new_source no_reward_live_general no_release_claim')
