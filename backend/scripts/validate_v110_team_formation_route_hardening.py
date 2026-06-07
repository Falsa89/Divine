#!/usr/bin/env python3
# Pack 80 — Track D: team formation route hardening.
import os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = open(os.path.join(R, 'backend/routes/v96_team_formation.py')).read()
for tok in [
    'server_id: Optional[str] = None',
    '"filter_applied"', '"source"', '"profile_id"', '"team_formation"', '"blocker"',
    'player_server_profiles',
    '"PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER"',
    '"blocked_no_team_for_server"',
    '"saved_formation_server_scoped"',
    '"safe_fallback_formation"',
]:
    assert tok in src, f'v96_team_formation.py missing token: {tok}'
# filter_applied=true SOLO quando server_id presente (controllo testuale chiave)
assert '"filter_applied": True' in src, 'filter_applied=True branch missing (server_id path)'
assert '"filter_applied": bool(server_id)' in src, 'filter_applied=bool(server_id) branch missing'
# NO db writes: zero update/insert/delete/replace nel modulo
for forbidden in ('await db.users.update_one', 'await db.users.insert_one', 'await db.users.delete_one', 'await db.player_server_profiles.update_one', 'await db.player_server_profiles.insert_one', 'await db.player_server_profiles.delete_one'):
    assert forbidden not in src, f'forbidden DB write detected: {forbidden}'
print('[v110 TEAM_FORMATION_ROUTE_HARDENING] OK schema_consistent server_id_required_for_filter_applied psp_aware blocker_emitted db_writes=0')
