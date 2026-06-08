#!/usr/bin/env python3
# Pack 83 - Track I: server lifecycle / fresh-start preservation.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sl = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_preflight/v110_psp_normalization_server_lifecycle_preservation_v1.json')))
scope = sl.get('normalization_scope_strictly_limited_to', [])
assert any('player_server_profiles.user_id' in s for s in scope), 'scope must be limited to user_id field'
not_touch = sl.get('normalization_does_NOT_touch', [])
for must in ('player_level', 'player_exp', 'story_progress', 'soft_currencies', 'team_formation', 'user_heroes', 'users'):
    assert any(must in s for s in not_touch), f'normalization_does_NOT_touch must include {must}'
copy = sl.get('does_NOT_copy_S1_to_S2', {})
for k in ('roster','player_level','player_exp','team_formation','story_progress','inventory','equipment'):
    assert copy.get(k) is True, f'does_NOT_copy_S1_to_S2.{k} must be true'
assert sl.get('does_NOT_create_new_server_PSP') is True
assert sl.get('does_NOT_create_new_user') is True
assert sl.get('fresh_start_invariant_unchanged_for_servers_never_played') is True
assert sl.get('server_player_progress_SOT_unchanged') is True
assert sl.get('dual_read_compat_remains_active_during_and_after') is True
print('[v110 PACK_83_SERVER_LIFECYCLE_PRESERVATION] OK scope_limited_user_id_only no_S1_to_S2_copy no_new_PSP_creation fresh_start_unchanged')
