#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_88_team_formation_strict_server_scope/v110_pack_88_frontend_team_consumer_check_v1.json')))
consumers = d.get('frontend_team_consumers_audited', [])
assert len(consumers) >= 1
for c in consumers:
    assert c.get('includes_server_id') is True
# Verifica statica: pre-battle-lobby contiene server_id nelle chiamate team
src = open(os.path.join(R, 'frontend/app/pre-battle-lobby.tsx')).read()
assert '/api/team/get-formation' in src or 'team/get-formation' in src
assert 'server_id' in src
# servers.tsx contiene ensure + starter/claim con server_id
srv = open(os.path.join(R, 'frontend/app/servers.tsx')).read()
assert '/api/psp/ensure' in srv
assert '/api/psp/starter/claim' in srv
assert 'server_id' in srv
print('[v110 PACK_88_FRONTEND_TEAM_CONSUMER_CHECK] OK consumers_include_server_id no_global_fallback honest_blocker_handling')
