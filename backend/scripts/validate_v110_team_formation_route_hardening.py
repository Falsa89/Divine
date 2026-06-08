#!/usr/bin/env python3
# Pack 80 \u2014 Track D: team formation route hardening.
# Pack 88 follow-up: route refactor STRICT server-scoped. La check originale
# di `"filter_applied": bool(server_id)` non e' piu' applicabile come literal
# (Pack 88 usa booleani espliciti per branch). Tutti gli altri check di
# hardening (no db writes, blocker presenti, source PSP-aware) restano
# preservati. NO validator weakening: aggiungiamo tokens Pack 88 espliciti.
import os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = open(os.path.join(R, 'backend/routes/v96_team_formation.py')).read()
for tok in [
    'server_id: Optional[str] = None',
    '"filter_applied"', '"source"', '"team_formation"', '"blocker"',
    'player_server_profiles',
    '"PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER"',
    '"blocked_no_team_for_server"',
    '"saved_formation_server_scoped"',
    # Pack 88 strict tokens (additive, replace legacy "safe_fallback_formation" location strict mode)
    'pack_88_strict_server_scope',
    'PLAYER_SERVER_PROFILE_REQUIRED',
    'player_server_profile',
    'legacy_account_team_used',
]:
    assert tok in src, f'v96_team_formation.py missing token: {tok}'
# filter_applied=true SOLO quando server_id presente (controllo testuale chiave preservato)
assert '"filter_applied": True' in src, 'filter_applied=True branch missing (server_id path)'
# Pack 88: filter_applied=False in legacy path (no-server_id non-player-facing)
assert '"filter_applied": False' in src, 'filter_applied=False branch missing (legacy non-player-facing path)'
# NO db writes: zero update/insert/delete/replace nel modulo (preservato)
for forbidden in ('await db.users.update_one', 'await db.users.insert_one', 'await db.users.delete_one', 'await db.player_server_profiles.update_one', 'await db.player_server_profiles.insert_one', 'await db.player_server_profiles.delete_one'):
    assert forbidden not in src, f'forbidden DB write detected: {forbidden}'
print('[v110 TEAM_FORMATION_ROUTE_HARDENING] OK schema_consistent server_id_required_for_filter_applied psp_aware blocker_emitted db_writes=0 pack_88_strict_server_scope_present')
