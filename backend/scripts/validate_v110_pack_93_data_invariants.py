#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_93_economy_progress_write_paths/v110_pack_93_data_invariants_v1.json')))
inv = d.get('invariants', {})
for k in ('pack_88_team_strict_preserved','pack_89_inventory_get_strict_preserved','pack_90_inventory_write_paths_strict_preserved','pack_91_inventory_frontend_consumer_migration_preserved','pack_92_core_server_scope_megapack_preserved'):
    assert inv.get(k) is True, k
for k in ('production_user_db_writes','broad_db_writes','migration_executed','backfill_executed','legacy_cleanup_executed','reward_live','progress_live','premium_grant','currency_grant','iap_store_payment_change','false_filter_applied_true','false_readiness','account_wide_writes_for_server_bound_data','s1_to_s2_copy','unmarked_test_writes','destructive_migration','release_readiness_claimed','fake_PASS','validator_weakening','postqa_d_gates_unlocked','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live'):
    assert inv.get(k) is False, k
print('[v110 PACK_93_DATA_INVARIANTS] OK pack_88_92_preserved all_negatives_false')
