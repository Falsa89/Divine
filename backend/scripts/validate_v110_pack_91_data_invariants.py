#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_91_inventory_frontend_consumer_and_smoke/v110_pack_91_data_invariants_v1.json')))
inv = d.get('invariants', {})
for k in ('no_production_user_db_writes',):
    assert inv.get(k) is True, k
for k in ('unmarked_test_writes','schema_migration_executed','backfill_executed','account_wide_inventory_write','hardcoded_s1_in_writes','frontend_mutation_without_server_id','silent_s1_fallback','copy_s1_to_s2_inventory','currencies_db_writes','story_db_writes','equipment_db_writes','reward_live','progress_live','premium_grant','currency_grant','legacy_cleanup_executed','destructive_migration','player_level_mutation','user_heroes_cross_server_mutation','team_route_regression','postqa_d_gates_unlocked','battle_engine_formula_rewrite','battle_simulate_called_from_staging_or_live','release_readiness_claimed'):
    assert inv.get(k) is False, k
print('[v110 PACK_91_DATA_INVARIANTS] OK no_production_writes all_negatives_false')
