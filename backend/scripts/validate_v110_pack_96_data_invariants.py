#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_96_reward_claim_ledger_live_execute/v110_pack_96_data_invariants_v1.json')))
for k in ('no_production_user_writes','no_unmarked_test_writes','no_premium_hard_currency_grants','no_reward_live_general','no_legacy_cleanup_general_execute','no_destructive_migration','no_broad_db_writes','pack_84_through_95_preserved','pack_91_inventory_preserved','pack_93_wallet_spend_preserved','pack_94_equipment_strict_preserved','pack_95_story_strict_preserved','pack_95_legacy_quarantine_preserved'):
    assert d.get(k) is True, k
assert d.get('test_artifact_marker_required') == 'pack_96_test_artifact'
print('[v110 PACK_96_DATA_INVARIANTS] OK no_production_writes no_premium_grants no_reward_live_general pack_84_95_preserved')
