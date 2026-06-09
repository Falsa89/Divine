#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_92_core_server_scope/v110_pack_92_data_invariants_v1.json')))
inv = d.get('invariants', {})
for k in ('pack_88_team_strict_preserved','pack_89_inventory_get_strict_preserved','pack_90_inventory_write_paths_strict_preserved','pack_91_inventory_frontend_consumer_migration_preserved'):
    assert inv.get(k) is True, k
for k in ('broad_db_writes','currency_write_promotion','story_progress_write_promotion','equipment_write_promotion','reward_live','progress_live','premium_grant','s1_to_s2_copy','legacy_cleanup_executed','destructive_migration','production_user_db_writes','schema_migration_executed','backfill_executed','account_wide_fallback_for_server_bound_data','silent_s1_fallback','copy_s1_to_s2_inventory','false_filter_applied_true','player_level_mutation','user_heroes_cross_server_mutation','team_route_regression','postqa_d_gates_unlocked','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','release_readiness_claimed','fake_PASS','validator_weakening'):
    assert inv.get(k) is False, k
print('[v110 PACK_92_DATA_INVARIANTS] OK pack_88_91_preserved all_negatives_false')
