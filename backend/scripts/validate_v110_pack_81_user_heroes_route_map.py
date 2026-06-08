#!/usr/bin/env python3
# Pack 81 - Track 3: runtime route map per /api/user/heroes.
import os, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
server_py = open(os.path.join(R, 'backend/server.py')).read()
# Productive route deve esistere in server.py con server_id Optional[str]
assert re.search(r"@app\.get\(\s*['\"]\/api\/user\/heroes['\"]\s*\)", server_py), 'productive /api/user/heroes decorator missing in server.py'
assert 'server_id: Optional[str] = None' in server_py, 'server_id Optional[str] param missing in productive route'
assert 'player_server_profiles' in server_py, 'PSP collection lookup missing in productive route'
# Probe route NON deve essere produttiva (controllo che resti marcata come probe)
probe_path = os.path.join(R, 'backend/routes/v107c_loader_server_id_probe.py')
if os.path.exists(probe_path):
    probe_src = open(probe_path).read()
    assert 'probe' in probe_src.lower(), 'probe route should remain labeled probe'
print('[v110 PACK_81_USER_HEROES_ROUTE_MAP] OK productive_route_in_server_py probe_route_isolated')
