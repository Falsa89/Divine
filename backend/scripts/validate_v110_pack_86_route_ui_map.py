#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_86_lobby_psp_ensure/v110_pack_86_route_ui_map_v1.json')))
assert d.get('backend_ensure_route', {}).get('path') == 'POST /api/psp/ensure?server_id=<sid>'
assert d.get('server_selection_ui', {}).get('primary_file') == 'frontend/app/servers.tsx'
assert d.get('pre_battle_lobby', {}).get('file') == 'frontend/app/pre-battle-lobby.tsx'
call_sites = d.get('pack_86_ensure_call_sites', [])
assert len(call_sites) >= 2
files = {c.get('file') for c in call_sites}
assert 'frontend/app/servers.tsx' in files
assert 'frontend/app/pre-battle-lobby.tsx' in files
reg = d.get('api_register_legacy_path', {})
assert reg.get('route') == 'POST /api/register'
assert 'DISABLED by default' in reg.get('pack_86_behavior', '') or 'disabled by default' in reg.get('pack_86_behavior', '').lower()
print('[v110 PACK_86_ROUTE_UI_MAP] OK backend_ensure_route_documented servers.tsx_and_lobby_call_sites_identified register_legacy_path_documented')
