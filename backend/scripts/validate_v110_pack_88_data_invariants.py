#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_88_team_formation_strict_server_scope/v110_pack_88_data_invariants_v1.json')))
for k in ('account_wide_team_fallback_when_server_id','writes_to_users_team_formation_in_server_scoped_flow','fake_team','fallback_global_roster_or_team','overwrite_existing_team','copy_s1_to_s2','user_heroes_mutation_outside_pack_87_starter_smoke','inventory_currency_story_equipment_mutation','bulk_psp_apply','physical_normalization','legacy_cleanup_executed','destructive_migration','delete_of_real_psp','delete_of_real_user_heroes','reward_live','progress_live','premium_grant','player_level_mutation','release_readiness_claimed'):
    assert d.get(k) is False, f'invariant {k} must be false'
print('[v110 PACK_88_DATA_INVARIANTS] OK no_account_wide_team_fallback_with_server_id no_users_team_formation_writes no_fake_team no_global_fallback no_overwrite no_legacy_cleanup no_reward/progress_live')
