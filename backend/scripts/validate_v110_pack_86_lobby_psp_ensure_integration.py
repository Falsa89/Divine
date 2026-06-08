#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_86_lobby_psp_ensure/v110_pack_86_lobby_psp_ensure_integration_v1.json')))
mods = d.get('frontend_files_modified', [])
assert 'frontend/app/servers.tsx' in mods
assert 'frontend/app/pre-battle-lobby.tsx' in mods
inv = d.get('invariants', {})
assert inv.get('explicit_server_id') is True
assert inv.get('bearer_required') is True
assert inv.get('idempotent') is True
assert inv.get('silent_s1') is False
assert inv.get('global_fallback_on_failure') is False
assert inv.get('copy_s1_to_s2') is False
# Verifica statica: i file frontend contengono effettivamente la chiamata
servers_src = open(os.path.join(R, 'frontend/app/servers.tsx')).read()
lobby_src = open(os.path.join(R, 'frontend/app/pre-battle-lobby.tsx')).read()
assert '/api/psp/ensure' in servers_src, 'servers.tsx must call /api/psp/ensure'
assert 'X-Pack-86-Frontend-Ensure' in servers_src, 'servers.tsx must mark Pack 86 frontend ensure'
assert '/api/psp/ensure' in lobby_src, 'lobby must call /api/psp/ensure'
assert 'X-Pack-86-Lobby-Defensive-Ensure' in lobby_src, 'lobby must mark Pack 86 defensive ensure'
# NO silent 's1' in the ensure call sites
import re
# Ensure that the ensure URL uses encodeURIComponent of the selected server, not hardcoded 's1'
assert "/api/psp/ensure?server_id=${encodeURIComponent(s.server_id)}" in servers_src
assert "/api/psp/ensure?server_id=${encodeURIComponent(selectedServerId)}" in lobby_src
print('[v110 PACK_86_LOBBY_PSP_ENSURE_INTEGRATION] OK servers.tsx_and_lobby_call_ensure no_silent_s1 idempotent_backend_pack85 no_global_fallback')
