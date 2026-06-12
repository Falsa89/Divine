#!/usr/bin/env python3
"""Pack 106 — Live readiness flags update."""
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
smoke_path = os.path.join(R, 'data/design/v110_pack_106_mail_achievements_daily_weekly_controlled_rewards/v110_pack_106_runtime_smoke_e2e_result_v1.json')
d = json.load(open(smoke_path))
expected = {
    'mail_claim_controlled_ready': True,
    'achievement_claim_controlled_ready': True,
    'daily_weekly_reward_claim_ready': True,
    'no_reward_live_general': True,
    'release_readiness_claimed': False,
    'no_battlepass_event_afk_pvp_guild_live': True,
}
for k, v in expected.items():
    assert d.get(k) == v, f'live readiness mismatch {k}: {d.get(k)} != {v}'
print('[v110 PACK_106_LIVE_READINESS_UPDATE] OK mail_ready achievement_ready daily_weekly_ready reward_live_general_false release_readiness_false no_battlepass_event_afk_pvp_guild_live')
