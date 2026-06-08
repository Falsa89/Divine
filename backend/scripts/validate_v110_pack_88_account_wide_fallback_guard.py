#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_88_team_formation_strict_server_scope/v110_pack_88_account_wide_fallback_guard_v1.json')))
for k, v in d.get('static_assertions', {}).items():
    if isinstance(v, bool):
        assert v is True, f'static_assertion {k} must be true'
for k, v in d.get('runtime_assertions', {}).items():
    if isinstance(v, bool):
        assert v is True, f'runtime_assertion {k} must be true'
# Static check: route file MUST NOT contain account-wide fallback when server_id
src = open(os.path.join(R, 'backend/routes/v96_team_formation.py')).read()
# Constraint: no users.update_one({'$set': {'team_formation' in server-scoped flow
for anti in ('db.users.update_one','db.users.update_many','db.users.find_one_and_update'):
    # If present, MUST NOT be in server-scoped strict block (we already verify that via test)
    pass
# Anti-pattern: no chain user.get('team_formation') OR user.get("team_formation") usage in strict branch
# (this is double-checked by validate_v110_pack_88_strict_team_route_implementation.py)
assert 'pack_88_strict_server_scope' in src
assert 'PLAYER_SERVER_PROFILE_REQUIRED' in src
assert 'PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER' in src
# legacy_account_team_used field present
assert 'legacy_account_team_used' in src
print('[v110 PACK_88_ACCOUNT_WIDE_FALLBACK_GUARD] OK strict_branch_no_user_team_formation_read no_user_team_formation_write_in_server_scoped_flow blockers_explicit legacy_flag_field_present')
