#!/usr/bin/env python3
# Pack 83 - Track K: zero mutation/economy preservation.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_psp_normalization_preflight/v110_psp_normalization_preflight_summary_v1.json')
d = json.load(open(S))
z = d.get('zero_mutation_economy_preservation', {})
for k in ('db_writes','psp_writes','user_heroes_writes','users_writes'):
    assert z.get(k) == 0, f'{k} must be 0'
for k in ('physical_normalization_executed','psp_apply','legacy_cleanup_executed','destructive_migration_executed','delete','premium_grant','reward_grant','progress_advance','user_heroes_mutation','player_level_mutation','s1_to_s2_copy','new_server_psp_creation_in_this_pack'):
    assert z.get(k) is False, f'{k} must be false'
# Static: nessun productive code runtime e' stato modificato in Pack 83
rf = d.get('runtime_files_modified', [])
assert rf == [] or len(rf) == 0, 'Pack 83 must be runtime-files-modified-count=0 (preflight only)'
assert d.get('runtime_files_modified_count', 1) == 0
print('[v110 PACK_83_ZERO_MUTATION_PRESERVATION] OK no_db_writes no_runtime_files_modified no_PSP_apply no_psp_writes')
