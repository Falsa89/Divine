#!/usr/bin/env python3
"""Pack 106 — Runtime smoke E2E result presence + integrity."""
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(R, 'data/design/v110_pack_106_mail_achievements_daily_weekly_controlled_rewards/v110_pack_106_runtime_smoke_e2e_result_v1.json')
assert os.path.exists(path), 'pack 106 smoke result missing'
d = json.load(open(path))
assert d['real_smoke_executed'] is True, f'smoke not green: {d.get("required_missing")}'
assert d['mail_claim_controlled_ready'] is True
assert d['achievement_claim_controlled_ready'] is True
assert d['daily_weekly_reward_claim_ready'] is True
assert d['s1_s2_isolation_verified'] is True
assert d['no_users_gold_gems_experience_mutation'] is True
assert d['no_premium_grant'] is True
assert d['no_iap_gacha_payment'] is True
assert d['no_battlepass_event_afk_pvp_guild_live'] is True
assert d['no_reward_live_general'] is True
assert d['release_readiness_claimed'] is False
assert d['client_payload_reward_grant_ignored'] is True
for required in ('mail_S1_success','mail_replay_idempotent','mail_S1_S2_isolated',
                 'achievement_completion_required','achievement_S1_success','achievement_replay_idempotent',
                 'daily_S1_success','daily_S1_same_day_idempotent','weekly_S1_success','s2_daily_weekly_unaffected',
                 'client_payload_ignored','users_invariant',
                 'no_battlepass_event_afk_pvp_guild_routes','pack_91_105_preserved'):
    assert d['proofs'].get(required) is True, f'missing proof: {required}'
print('[v110 PACK_106_RUNTIME_SMOKE_E2E] OK mail_ready achievement_ready daily_weekly_ready S1_S2_isolated completion_required_works client_payload_ignored no_battlepass_event_afk_pvp_guild_live')
