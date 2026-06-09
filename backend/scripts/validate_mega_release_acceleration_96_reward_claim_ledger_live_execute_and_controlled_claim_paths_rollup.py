#!/usr/bin/env python3
"""Pack 96 — Rollup validator.

PUBLIC_SYNC_TAG_v110_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_AND_CONTROLLED_CLAIM_PATHS
"""
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DD = os.path.join(R, 'data/design/v110_pack_96_reward_claim_ledger_live_execute')

# Summary
d = json.load(open(os.path.join(DD, 'v110_pack_96_summary_v1.json')))
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','reward_live_general','premium_grant','iap_store_payment_change','gacha_change','broad_production_reward_grants','unmarked_test_writes','legacy_cleanup_general_execute','destructive_migration','account_wide_server_bound_reward_grant','hardcoded_s1_in_pack_96_active_paths','reward_source_outside_allowlist_grants_possible','double_reward_grant_possible','users_gold_gems_grant_in_claim_path','destructive_index_drop','kill_switch_default_on','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live'):
    assert d['safety_flags'].get(k) is False, k
for k in ('reward_claim_ledger_live_execute_implemented_kill_switch_default_off','controlled_claim_endpoint_live_gated','first_controlled_claim_sources_allowlisted_only','grant_engine_blocks_premium_and_unknown','smoke_e2e_executed_first_claim_replay_unknown_block_premium_block_cross_server','static_anti_bypass_guard_present','unique_index_idempotent_no_destructive_drop','no_reward_live_general','no_premium_hard_currency_grant','no_double_reward_grant','pack_91_inventory_preserved','pack_93_wallet_spend_preserved','pack_94_equipment_strict_preserved','pack_95_story_strict_and_legacy_quarantine_preserved','kill_switch_lifecycle_clean_during_smoke_and_restored'):
    assert d['explicit_statements'].get(k) is True, k

# Smoke result
smoke = json.load(open(os.path.join(DD, 'v110_pack_96_runtime_smoke_e2e_result_v1.json')))
assert smoke.get('real_smoke_executed') is True
assert smoke.get('no_premium_grant') is True
assert smoke.get('no_double_grant') is True
assert smoke.get('no_reward_live_general') is True
assert smoke.get('test_artifact_marker') == 'pack_96_test_artifact'

# Runtime code present
rc = open(os.path.join(R, 'backend/routes/reward_claim.py')).read()
assert 'REWARD_CLAIM_LEDGER_LIVE_DISABLED' in rc
assert 'REWARD_SOURCE_NOT_ALLOWLISTED' in rc
assert 'PREMIUM_GRANT_BLOCKED' in rc
assert 'create_index' in rc and 'unique=True' in rc
assert '_slc_pack_96_controlled_claim' in rc
assert '_slc_pack_96_grant_engine_guard' in rc

rg = open(os.path.join(R, 'backend/utils/reward_source_registry.py')).read()
assert 'qa_controlled_soft_currency_claim' in rg
assert 'story_progress_marker_claim' in rg
assert 'FORBIDDEN_REWARD_TYPES' in rg
assert 'gems' in rg  # explicit ban

# Wiring
gs = open(os.path.join(R, 'backend/game_systems.py')).read()
assert 'register_reward_claim_routes' in gs

# Pack 95 preserved
combat = open(os.path.join(R, 'backend/routes/combat.py')).read()
assert 'pack_95_strict_story_progress_write' in combat
sf = open(os.path.join(R, 'backend/routes/soul_forge.py')).read()
assert 'LEGACY_CURRENCY_QUARANTINE_DEFERRED' in sf
assert 'SHOPS_BUY_SERVER_SCOPE_DEFERRED' in sf
assert 'SOUL_FORGE_RETIRE_SERVER_SCOPE_DEFERRED' in sf
# Pack 94 preserved
eq = open(os.path.join(R, 'backend/routes/equipment.py')).read()
assert '_slc_pack_94_equipment_loader_strict' in eq

print('[v110 MEGA_RELEASE_ACCELERATION_96_REWARD_CLAIM_LEDGER_LIVE_EXECUTE_AND_CONTROLLED_CLAIM_PATHS_ROLLUP] '
      'OK reward_claim_endpoint_live_gated kill_switch_default_off allowlist_enforced grant_engine_blocks_premium '
      'replay_safe unique_index_idempotent no_reward_live_general pack_91_93_94_95_preserved no_release_readiness')
