#!/usr/bin/env python3
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_data_invariants_v1.json')))
for k in ('no_production_broad_grants','no_unmarked_test_writes','no_premium_hard_currency_grants','no_gacha_iap_changes','no_legacy_cleanup_general_execute','no_destructive_migration','pack_84_through_97_preserved','production_user_safety_marker_check_on_test_overrides','completion_proof_required_for_real_users'):
    assert d[k] is True, k
assert d['reward_live_general'] is False
print('[v110 PACK_98_DATA_INVARIANTS] OK no_broad_grants no_premium no_reward_live_general completion_proof_required pack_84_97_preserved')
