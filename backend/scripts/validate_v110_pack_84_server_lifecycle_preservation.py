#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_execute/v110_psp_normalization_execute_summary_v1.json')))
l = d.get('server_lifecycle_preservation_post_execute', {})
for k in ('server_id','profile_id','player_level','player_exp','story_progress','soft_currencies','team_formation'):
    assert k in l.get('fields_NOT_touched_in_psp', []), f'{k} must be in NOT_touched list'
for k in ('user_heroes_writes','users_writes','battle_history_writes','inventory_writes','equipment_writes','any_other_collection_writes'):
    assert l.get(k) == 0, f'{k} must be 0'
assert l.get('no_s1_to_s2_copy_executed') is True
assert l.get('no_new_server_psp_created') is True
assert l.get('fresh_start_invariant_preserved') is True
assert l.get('server_player_progress_sot_preserved') is True
print('[v110 PACK_84_SERVER_LIFECYCLE_PRESERVATION] OK fields_NOT_touched=7 user_heroes_writes=0 users_writes=0 no_s1_to_s2 no_new_PSP fresh_start_preserved')
