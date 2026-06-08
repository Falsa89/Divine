#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_87_server_scoped_starter_flow/v110_pack_87_data_invariants_v1.json')))
for k in ('account_wide_starter_from_register','copy_s1_to_s2','player_level_mutation','premium_currency_grant','hard_currency_grant','inventory_grant','equipment_grant','story_reward_grant','legacy_cleanup_executed','destructive_migration','delete_of_real_psp','bulk_psp_apply','physical_normalization_executed_in_this_pack','team_overwrite_existing','reward_live','progress_live','release_readiness_claimed'):
    assert d.get(k) is False, f'invariant {k} must be false'
for k in ('starter_user_heroes_only_on_selected_server','all_starter_user_heroes_include_server_id','starter_user_heroes_creation_source_pack_87','team_init_only_if_empty'):
    assert d.get(k) is True, f'invariant {k} must be true'
net = d.get('net_db_writes_during_smoke_test', {})
assert net.get('users') == 0
assert net.get('user_heroes') == 0
assert net.get('player_server_profiles') == 0
print('[v110 PACK_87_DATA_INVARIANTS] OK no_account_wide_starter no_s1_to_s2 no_player_level_mutation no_premium_currency no_inventory_equipment_story_reward no_overwrite_team no_legacy_cleanup net_smoke_delta=0')
