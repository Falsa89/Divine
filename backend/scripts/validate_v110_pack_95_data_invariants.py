#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_95_reward_ledger_story_write_legacy_guards/v110_pack_95_data_invariants_v1.json')))
for k in ('no_production_user_writes','no_unmarked_test_writes','no_premium_hard_currency_grants','no_reward_live','no_legacy_cleanup_general_execute','no_destructive_migration','no_broad_db_writes','pack_84_through_94_preserved','pack_91_inventory_preserved','pack_93_wallet_spend_preserved','pack_94_equipment_strict_preserved','pack_94_legacy_earn_pvp_guild_quarantine_preserved'):
    assert d.get(k) is True, k
assert d.get('test_artifact_marker_required') == 'pack_95_test_artifact'
print('[v110 PACK_95_DATA_INVARIANTS] OK no_production_writes no_premium_grant no_reward_live pack_84_94_preserved')
