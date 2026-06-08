#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_88_team_formation_strict_server_scope/v110_pack_88_team_formation_source_audit_v1.json')))
aud = d.get('audit_results', {})
routes = aud.get('team_routes_identified', [])
assert len(routes) >= 1
assert any(r.get('path') == 'GET /api/team/get-formation' for r in routes)
loc = aud.get('team_field_locations', {})
legacy = loc.get('account_wide_legacy', {})
assert legacy.get('player_facing_status', '').upper().startswith('DEPRECATED')
assert legacy.get('writes_in_server_scoped_flow') is False
ss = loc.get('server_scoped', {})
assert ss.get('player_facing_status') == 'AUTHORITATIVE'
assert ss.get('writes_only_if_empty') is True
start = aud.get('pack_87_starter_team_init_path', {})
assert start.get('preserved') is True
print('[v110 PACK_88_TEAM_FORMATION_SOURCE_AUDIT] OK team_route_identified legacy_field_deprecated psp_authoritative pack_87_starter_preserved')
