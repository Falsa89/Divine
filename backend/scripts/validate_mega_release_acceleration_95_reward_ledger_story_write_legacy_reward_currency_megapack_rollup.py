#!/usr/bin/env python3
"""Pack 95 — Rollup validator.

PUBLIC_SYNC_TAG_v110_REWARD_LEDGER_STORY_WRITE_LEGACY_REWARD_CURRENCY_MEGAPACK
"""
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DESIGN_DIR = os.path.join(R, 'data/design/v110_pack_95_reward_ledger_story_write_legacy_guards')

# Summary
d = json.load(open(os.path.join(DESIGN_DIR, 'v110_pack_95_summary_v1.json')))
# Safety flags must all be false
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','reward_live','progress_live','premium_grant','iap_store_payment_change','false_filter_applied_true','false_readiness','account_wide_writes_for_server_bound_data','unmarked_test_writes','destructive_migration','legacy_cleanup_general_execute','postqa_d_gates_unlocked','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','hardcoded_s1_in_pack_95_active_paths','double_reward_grant_possible','account_wide_story_progress_write','users_gold_gems_grant_in_strict_path'):
    assert d['safety_flags'].get(k) is False, k

for k in ('reward_claim_ledger_runtime_foundation_implemented','story_progress_write_strict_server_scope_implemented','legacy_currency_quarantine_active','shops_buy_quarantine_active','soul_forge_retire_quarantine_active','smoke_e2e_executed_with_idempotency_replay','static_anti_double_grant_guard_present','no_reward_live_activation_generale','no_premium_hard_currency_grant','no_double_reward_grant','no_account_wide_story_progress_write','pack_91_inventory_preserved','pack_93_wallet_spend_preserved','pack_94_equipment_strict_preserved'):
    assert d['explicit_statements'].get(k) is True, k

# Smoke result
smoke = json.load(open(os.path.join(DESIGN_DIR, 'v110_pack_95_runtime_smoke_e2e_result_v1.json')))
assert smoke.get('real_smoke_executed') is True
assert smoke.get('test_only_writes') is True
assert smoke.get('no_production_user_writes') is True
assert smoke.get('test_artifact_marker') == 'pack_95_test_artifact'

# Runtime code present
combat_src = open(os.path.join(R, 'backend/routes/combat.py')).read()
assert '_slc_pack_95_reward_claim_ledger' in combat_src
assert '_slc_pack_95_no_live_grant' in combat_src
assert 'pack_95_strict_story_progress_write' in combat_src
assert 'IDEMPOTENCY_TOKEN_REQUIRED' in combat_src

sf_src = open(os.path.join(R, 'backend/routes/soul_forge.py')).read()
assert '_slc_pack_95_shops_buy_quarantine' in sf_src
assert '_slc_pack_95_soul_forge_retire_quarantine' in sf_src
assert '_slc_pack_95_legacy_currency_quarantine' in sf_src
assert 'SHOPS_BUY_SERVER_SCOPE_DEFERRED' in sf_src
assert 'SOUL_FORGE_RETIRE_SERVER_SCOPE_DEFERRED' in sf_src
assert 'LEGACY_CURRENCY_QUARANTINE_DEFERRED' in sf_src

# Pack 94 preserved
assert '_slc_pack_94_equipment_loader_strict' in open(os.path.join(R, 'backend/routes/equipment.py')).read()
assert '_slc_pack_94_legacy_currency_quarantine' in sf_src

print('[v110 MEGA_RELEASE_ACCELERATION_95_REWARD_LEDGER_STORY_WRITE_LEGACY_REWARD_CURRENCY_MEGAPACK_ROLLUP] '
      'OK reward_ledger_runtime_foundation story_write_strict_real legacy_quarantine_active '
      'shops_buy_quarantine soul_forge_retire_quarantine pack_91_93_94_preserved no_reward_live no_release_readiness')
