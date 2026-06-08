#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_86_lobby_psp_ensure/v110_pack_86_user_heroes_team_after_ui_ensure_v1.json')))
h = d.get('post_ensure_user_heroes', {})
assert h.get('x_filter_applied') == 'true'
assert h.get('x_psp_lookup_mode') == 'direct_uuid'
assert h.get('x_player_level') == '1'
assert h.get('x_player_exp') == '0'
assert h.get('roster_count') == 0
assert h.get('fresh_start_preserved') is True
assert h.get('no_global_fallback') is True
t = d.get('post_ensure_team', {})
assert t.get('team_formation') == []
assert t.get('team_not_configured_honestly') is True
assert t.get('no_global_fallback') is True
tr = d.get('transitions', {})
assert tr.get('pre_ensure_blocker') == 'PLAYER_SERVER_PROFILE_REQUIRED'
assert tr.get('post_ensure_blocker') == ''
print('[v110 PACK_86_USER_HEROES_TEAM_AFTER_UI_ENSURE] OK heroes_filter_applied=true direct_uuid level=1 exp=0 roster=0 team_empty_honest')
