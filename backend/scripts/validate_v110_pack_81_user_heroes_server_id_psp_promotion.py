#!/usr/bin/env python3
# Pack 81 - Track 4: /api/user/heroes server_id/PSP promotion (static checks).
import os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = open(os.path.join(R, 'backend/server.py')).read()
# Real filter su {user_id, server_id}
assert 'db.user_heroes.find({"user_id": uid, "server_id": sid})' in src, 'real server_id filter missing'
# PSP-aware
assert 'db.player_server_profiles.find_one({"user_id": uid, "server_id": sid})' in src, 'PSP-aware lookup missing'
# Blocker headers
for must in ('PLAYER_SERVER_PROFILE_REQUIRED', 'SELECTED_SERVER_REQUIRED_FOR_PLAYER_FACING', 'account_wide_legacy_DEPRECATED', 'server_scoped_psp_filtered', 'server_scoped_no_psp_blocked'):
    assert must in src, f'route missing blocker/label: {must}'
for h in ('X-Server-Scope', 'X-Filter-Applied', 'X-Server-Id', 'X-Profile-Id', 'X-Blocker', 'X-Canonical-Decision', 'X-Roster-Source', 'X-Roster-Count'):
    assert f'"{h}"' in src, f'response header missing: {h}'
# filter_applied=true SOLO con server_id reale
assert 'response.headers["X-Filter-Applied"] = "true"' in src, 'true filter_applied branch missing'
assert 'response.headers["X-Filter-Applied"] = "false"' in src, 'false filter_applied branch missing'
# Canonical decision marker
assert 'user_heroes_are_server_scoped' in src, 'canonical decision marker missing'
print('[v110 PACK_81_USER_HEROES_SERVER_ID_PSP_PROMOTION] OK real_filter psp_aware blockers headers canonical_decision present')
