#!/usr/bin/env python3
import os, json, hashlib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_94_equipment_backfill_strict_currency_quarantine/v110_pack_94_summary_v1.json')))
for k in ('fake_PASS','validator_weakening','release_readiness_claimed','reward_live','progress_live','premium_grant','iap_store_payment_change','false_filter_applied_true','false_readiness','account_wide_writes_for_server_bound_data','s1_to_s2_equipment_copy','unmarked_test_writes','destructive_migration','non_equipment_broad_migration_backfill','legacy_cleanup_general_execute','postqa_d_gates_unlocked','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','hardcoded_s1_in_new_active_currency_equipment_write_paths'):
    assert d['safety_flags'].get(k) is False, k
for k in ('equipment_backfill_executed','db_writes_count_28_target_user_equipment','no_reward_progress_live','no_legacy_cleanup_general_execute','no_release_readiness_claim','pack_90_91_92_93_preserved','equipment_loader_strict_real_filter','equipment_write_strict_real','legacy_currency_quarantine_active'):
    assert d['explicit_statements'].get(k) is True, k
assert d['backfill'].get('executed') is True and d['backfill'].get('coverage_pct_post') == 100.0 and d['backfill'].get('docs_updated') == 28
assert d['backfill'].get('target_collection') == 'user_equipment'
smoke = json.load(open(os.path.join(R, 'data/design/v110_pack_94_equipment_backfill_strict_currency_quarantine/v110_pack_94_runtime_smoke_e2e_result_v1.json')))
assert smoke.get('real_smoke_executed') is True
eq_src = open(os.path.join(R, 'backend/routes/equipment.py')).read()
assert '_slc_pack_94_equipment_loader_strict' in eq_src and '_slc_pack_94_equipment_strict_write' in eq_src
assert 'EQUIPMENT_SERVER_SCOPED_LOADER_PROMOTION_DEFERRED' not in eq_src.split('async def get_user_equipment')[1].split('async def')[0]
sf_src = open(os.path.join(R, 'backend/routes/soul_forge.py')).read()
assert 'LEGACY_CURRENCY_QUARANTINE_DEFERRED' in sf_src
assert 'wallet_spend_ledger' in sf_src
print('[v110 MEGA_RELEASE_ACCELERATION_94_EQUIPMENT_BACKFILL_STRICT_SCOPE_AND_LEGACY_CURRENCY_QUARANTINE_ROLLUP] OK backfill_executed=28docs coverage_post=100 loader_strict_real write_strict_real legacy_currency_quarantine_active pack_90_93_preserved')
