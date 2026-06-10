#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_97_daily_login_claim_frontend_unlock/v110_pack_97_data_invariants_v1.json')))
for k in ('no_production_broad_grants','no_unmarked_test_writes','no_premium_hard_currency_grants','no_gacha_iap_changes','no_legacy_cleanup_general_execute','no_destructive_migration','pack_84_through_96_preserved','production_user_safety_marker_check_on_test_overrides'):
    assert d[k] is True, k
assert d['reward_live_general'] is False
assert d['test_artifact_marker_required'] == 'pack_97_test_artifact'
print('[v110 PACK_97_DATA_INVARIANTS] OK no_broad_grants no_premium no_reward_live_general pack_84_96_preserved')
