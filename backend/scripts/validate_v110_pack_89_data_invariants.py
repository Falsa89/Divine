#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_89_inventory_psp_scoped/v110_pack_89_data_invariants_v1.json')))
for k in ('inventory_schema_migration_executed','inventory_backfill_executed','inventory_db_writes_in_promotion_path','currencies_db_writes','story_db_writes','equipment_db_writes','false_filter_applied_true','account_wide_inventory_leak','copy_s1_to_s2','premium_grant','currency_grant','reward_live','progress_live','legacy_cleanup_executed','destructive_migration','delete_of_real_data','player_level_mutation','user_heroes_mutation','team_route_regression','release_readiness_claimed'):
    assert d.get(k) is False, f'invariant {k} must be false'
print('[v110 PACK_89_DATA_INVARIANTS] OK no_inventory_migration no_db_writes no_leak no_copy_s1_to_s2 no_reward/progress_live no_legacy_cleanup no_team_route_regression')
