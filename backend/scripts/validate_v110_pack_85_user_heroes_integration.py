#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_85_psp_onboarding/v110_pack_85_psp_onboarding_summary_v1.json')))
i = d.get('api_user_heroes_integration', {})
pre = i.get('pre_ensure_new_server_response', {})
post = i.get('post_ensure_new_server_response', {})
assert pre.get('X-Blocker') == 'PLAYER_SERVER_PROFILE_REQUIRED'
assert pre.get('X-Filter-Applied') == 'false'
assert pre.get('roster_count') == 0
assert post.get('X-Filter-Applied') == 'true'
assert post.get('X-PSP-Lookup-Mode') == 'direct_uuid'
assert post.get('X-Player-Level') == '1'
assert post.get('X-Player-Exp') == '0'
assert post.get('roster_count') == 0
assert i.get('transition_verified') is True
print('[v110 PACK_85_USER_HEROES_INTEGRATION] OK pre_blocker post_filter_applied=true post_lookup=direct_uuid level=1 exp=0 roster=0')
