#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_97_daily_login_claim_frontend_unlock/v110_pack_97_frontend_consumer_unlock_v1.json')))
assert d['feature_flag_env'] == 'EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED'
assert d['feature_flag_default'] == 'false'
assert d['visible_in_production_by_default'] is False
assert d['no_mail_achievements_battlepass_event_afk_consumers_in_pack_97'] is True
btn = os.path.join(R, 'frontend/src/components/DailyLoginClaimButton.tsx')
preview = os.path.join(R, 'frontend/app/daily-login-preview.tsx')
assert os.path.exists(btn) and os.path.exists(preview)
src = open(btn).read()
# Required gates and states
assert 'EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED' in src
assert 'useServerScope' in src
assert "if (!UI_ENABLED && !forceVisible) return null" in src
assert "if (!serverId) return null" in src
assert "if (!token) return null" in src
for st in ['idle', 'loading', 'claimed', 'already_claimed', 'kill_switch_off', 'psp_missing', 'error']:
    assert st in src, st
# Must NOT contain other claim source consumers
for banned in ['mail_reward_claim', 'achievements_claim', 'battlepass_claim', 'event_claim', 'afk_claim']:
    assert banned not in src, f'banned consumer: {banned}'
print('[v110 PACK_97_FRONTEND_CONSUMER_UNLOCK] OK feature_flag_default_off gates_complete states_complete no_other_consumers')
