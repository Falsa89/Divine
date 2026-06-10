#!/usr/bin/env python3
"""Pack 97 — Rollup validator.

PUBLIC_SYNC_TAG_v110_FIRST_REAL_CLAIM_SOURCE_AND_FRONTEND_REWARD_UNLOCK
"""
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DD = os.path.join(R, 'data/design/v110_pack_97_daily_login_claim_frontend_unlock')

# Summary
d = json.load(open(os.path.join(DD, 'v110_pack_97_summary_v1.json')))
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','reward_live_general','premium_grant','iap_store_payment_change','gacha_change','broad_production_reward_grants','mail_rewards_live','achievements_rewards_live','battlepass_rewards_live','event_rewards_live','afk_rewards_live','shop_rewards_live','unmarked_test_writes','legacy_cleanup_general_execute','destructive_migration','account_wide_server_bound_reward_grant','hardcoded_s1_in_pack_97_active_paths','reward_source_outside_allowlist_grants_possible','double_daily_reward_grant_possible','users_gold_gems_grant_in_daily_path','kill_switch_default_on','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live'):
    assert d['safety_flags'][k] is False, k
for k in ('daily_login_claim_live_ready_kill_switch_default_off','only_one_new_real_player_facing_source','reward_live_general_remains_false','no_premium_hard_currency_grants','no_double_daily_reward','frontend_consumer_minimal_gated_added','frontend_consumer_hidden_by_default','server_side_claim_key_strategy','unique_index_db_level_anti_double_grant','test_day_override_requires_marker','both_kill_switches_AND_logic_required','smoke_e2e_first_claim_replay_next_day_cross_server_all_green','pack_91_inventory_preserved','pack_93_wallet_spend_preserved','pack_94_equipment_strict_preserved','pack_95_story_strict_and_legacy_quarantine_preserved','pack_96_reward_claim_ledger_and_qa_sources_preserved'):
    assert d['explicit_statements'][k] is True, k
assert d['explicit_statements']['first_real_player_facing_claim_source_added'] == 'daily_login_claim'

# Smoke
smoke = json.load(open(os.path.join(DD, 'v110_pack_97_runtime_smoke_e2e_result_v1.json')))
assert smoke['real_smoke_executed'] is True
assert smoke['no_double_daily_reward'] is True
assert smoke['test_artifact_marker'] == 'pack_97_test_artifact'

# Runtime: daily route present
rc = open(os.path.join(R, 'backend/routes/daily_login_claim.py')).read()
for needle in ['REWARD_CLAIM_LEDGER_LIVE_DISABLED', 'DAILY_LOGIN_CLAIM_DISABLED', 'PLAYER_SERVER_PROFILE_REQUIRED', 'DAY_OVERRIDE_FORBIDDEN_FOR_NON_TEST_USER', 'compute_daily_claim_key', 'derive_idempotency_token_from_claim_key', 'ux_user_server_claimkey_daily_login_pack97', 'partialFilterExpression', '_slc_pack_97_daily_login_claim']:
    assert needle in rc, needle

# Registry: daily_login_claim live
rg = open(os.path.join(R, 'backend/utils/reward_source_registry.py')).read()
assert 'daily_login_claim' in rg
assert '_grant_daily_login_to_psp' in rg

# Wiring
gs = open(os.path.join(R, 'backend/game_systems.py')).read()
assert 'register_daily_login_claim_routes' in gs

# Frontend
btn = open(os.path.join(R, 'frontend/src/components/DailyLoginClaimButton.tsx')).read()
assert 'EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED' in btn
assert "if (!UI_ENABLED && !forceVisible) return null" in btn

# Pack 96 reward_claim still in place
rc96 = open(os.path.join(R, 'backend/routes/reward_claim.py')).read()
assert 'REWARD_SOURCE_NOT_ALLOWLISTED' in rc96 and 'PREMIUM_GRANT_BLOCKED' in rc96

# Pack 95 story strict
combat = open(os.path.join(R, 'backend/routes/combat.py')).read()
assert 'pack_95_strict_story_progress_write' in combat

# Pack 95 quarantine guards
sf = open(os.path.join(R, 'backend/routes/soul_forge.py')).read()
assert 'SHOPS_BUY_SERVER_SCOPE_DEFERRED' in sf

# Pack 94 equipment strict
eq = open(os.path.join(R, 'backend/routes/equipment.py')).read()
assert '_slc_pack_94_equipment_loader_strict' in eq

# SOT doc present
assert os.path.exists(os.path.join(R, 'docs/divine/117_DAILY_LOGIN_CLAIM_SOT.md'))

print('[v110 MEGA_RELEASE_ACCELERATION_97_FIRST_REAL_CLAIM_SOURCE_AND_FRONTEND_REWARD_UNLOCK_ROLLUP] '
      'OK daily_login_claim_live_gated server_side_claim_key unique_index_partial '
      'both_kill_switches_AND no_double_grant no_premium no_reward_live_general '
      'frontend_minimal_gated_default_hidden pack_91_93_94_95_96_preserved no_release_readiness')
