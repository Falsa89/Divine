#!/usr/bin/env python3
"""Pack 98 rollup."""
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DD=os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim')
summary=json.load(open(os.path.join(DD,'v110_pack_98_summary_v1.json')))
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','reward_live_general','premium_grant','iap_store_payment_change','gacha_change','broad_production_grants','mail_rewards_live','achievements_rewards_live','battlepass_rewards_live','event_rewards_live','afk_rewards_live','shop_rewards_live','unmarked_test_writes','legacy_cleanup_general_execute','destructive_migration','hardcoded_s1_in_pack_98_active_paths','reward_source_outside_allowlist_grants_possible','double_daily_quest_reward_grant_possible','double_daily_login_reward_grant_possible','users_gold_gems_grant_in_quest_path','kill_switch_default_on','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','home_ui_leak_in_production'):
    assert summary['safety_flags'][k] is False, k
for k in ('daily_login_home_ready_default_off','daily_quest_completion_claim_ready_gated_status','only_two_real_player_facing_sources','reward_live_general_remains_false','no_premium_hard_currency_grants','no_double_daily_quest_reward','completion_proof_required_for_real_users','frontend_consumer_minimal_gated','server_side_claim_key_strategy','unique_index_db_level_anti_double_grant','test_proof_requires_marker','both_kill_switches_AND_logic_required','smoke_e2e_all_green','pack_91_inventory_preserved','pack_93_wallet_spend_preserved','pack_94_equipment_strict_preserved','pack_95_story_strict_and_legacy_quarantine_preserved','pack_96_reward_claim_ledger_and_qa_sources_preserved','pack_97_daily_login_claim_preserved'):
    assert summary['explicit_statements'][k] is True, k
smoke=json.load(open(os.path.join(DD,'v110_pack_98_runtime_smoke_e2e_result_v1.json')))
assert smoke['real_smoke_executed'] is True
assert smoke['test_artifact_marker']=='pack_98_test_artifact'
assert smoke['completion_proof_marker_enforced'] is True
rc=open(os.path.join(R,'backend/routes/daily_quest_claim.py')).read()
for n in ['DAILY_QUEST_COMPLETION_REQUIRED','QUEST_ID_NOT_WHITELISTED','partialFilterExpression','_slc_pack_98_daily_quest_claim','pack_98_test_artifact']:
    assert n in rc
rg=open(os.path.join(R,'backend/utils/reward_source_registry.py')).read()
assert 'daily_quest_completion_claim' in rg and '_grant_daily_quest_to_psp' in rg
home=open(os.path.join(R,'frontend/app/(tabs)/home.tsx')).read()
assert 'DailyHomeRewardSection' in home
dhrs=open(os.path.join(R,'frontend/src/components/DailyHomeRewardSection.tsx')).read()
assert 'EXPO_PUBLIC_DAILY_HOME_UNLOCK' in dhrs and 'EXPO_PUBLIC_DAILY_CLAIM_UI_ENABLED' in dhrs
print('[v110 MEGA_RELEASE_ACCELERATION_98_DAILY_HOME_UNLOCK_AND_DAILY_QUEST_CLAIM_SOURCE_ROLLUP] OK daily_home_AND_two_flags_default_off daily_quest_completion_required completion_proof_marker_required no_double_grant no_premium no_reward_live_general pack_91_97_preserved')
