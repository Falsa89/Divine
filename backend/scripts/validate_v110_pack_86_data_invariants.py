#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_86_lobby_psp_ensure/v110_pack_86_data_invariants_v1.json')))
for k in ('bulk_psp_apply','physical_normalization_executed_in_this_pack','legacy_cleanup_executed','starter_heroes_created','starter_flow_approved','player_level_mutation_on_existing_psp','copy_s1_to_s2','inventory_mutation','story_mutation','equipment_mutation','reward_live','progress_live','premium_grant','destructive_migration','delete_of_real_psp'):
    assert d.get(k) is False, f'{k} must be false'
for k in ('user_heroes_writes_from_register','battle_history_writes','net_users_delta','net_psp_delta'):
    assert d.get(k) == 0, f'{k} must be 0'
print('[v110 PACK_86_DATA_INVARIANTS] OK user_heroes_writes_from_register=0 starter_heroes_created=false copy_s1_to_s2=false legacy_cleanup=false reward/progress live=false net_delta=0')
