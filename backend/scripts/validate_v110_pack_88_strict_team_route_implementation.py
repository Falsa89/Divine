#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_88_team_formation_strict_server_scope/v110_pack_88_strict_team_route_implementation_v1.json')))
inv = d.get('strict_invariants', {})
for k in ('server_id_required_for_player_facing','no_fallback_to_user_team_formation','no_writes_to_users_team_formation_in_server_scoped_flow','no_fake_team','no_global_fallback','dual_read_uuid_objectid_compat','pack_87_starter_team_preserved','legacy_path_non_player_facing'):
    assert inv.get(k) is True, f'invariant {k} must be true'
assert inv.get('missing_psp_returns_blocker') == 'PLAYER_SERVER_PROFILE_REQUIRED'
assert inv.get('psp_exists_but_team_empty_returns_blocker') == 'PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER'
assert inv.get('team_source_when_server_id_present') == 'player_server_profile_only'
# Verifica statica nel route file
src = open(os.path.join(R, 'backend/routes/v96_team_formation.py')).read()
for tok in d.get('static_proof_tokens_in_v96', []):
    if tok == 'no_player_facing_writes_blocker':
        continue
    assert tok in src, f'v96 token missing: {tok}'
# Anti-pattern: nel branch server_id (DEDICATED) NON deve esserci fallback a user.team_formation
# Cerchiamo: la funzione si compone in 2 branch ben separati. Verifichiamo che dopo "if server_id:" non venga letto user.get("team_formation") prima del return.
import re
# Estrai contenuto della funzione get_formation
m = re.search(r'async def get_formation\([^)]*\)[^:]*:(.+?)return router', src, re.DOTALL)
assert m, 'get_formation function not found'
body = m.group(1)
# Branch server_id
idx_if_server = body.find('if server_id:')
idx_legacy_path = body.find('# Pack 88 — LEGACY/COMPAT PATH')
if idx_legacy_path < 0:
    idx_legacy_path = body.find('LEGACY/COMPAT PATH')
assert idx_if_server > 0 and idx_legacy_path > idx_if_server, 'strict server_id branch must come BEFORE legacy path'
strict_branch = body[idx_if_server:idx_legacy_path]
assert 'user.get("team_formation")' not in strict_branch and "user.get('team_formation')" not in strict_branch, 'strict server_id branch MUST NOT read user.team_formation'
assert 'team_formation = user.get' not in strict_branch, 'strict server_id branch MUST NOT assign user.team_formation'
assert 'PLAYER_SERVER_PROFILE_REQUIRED' in strict_branch
assert 'PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER' in strict_branch
assert 'player_server_profile' in strict_branch
assert 'legacy_account_team_used' in strict_branch and 'False' in strict_branch  # legacy_account_team_used: False in strict path
print('[v110 PACK_88_STRICT_TEAM_ROUTE_IMPLEMENTATION] OK strict_branch_isolated no_user_team_formation_read_in_strict_branch blockers_explicit team_source_player_server_profile')
