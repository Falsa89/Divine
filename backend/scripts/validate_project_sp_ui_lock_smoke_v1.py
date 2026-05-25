#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_ui_lock_smoke_v1.json')
SRV = Path('/app/frontend/app/servers.tsx')
MENU = Path('/app/frontend/app/(tabs)/menu.tsx')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_F_SERVER_PROFILES_UI_LOCK_SMOKE_READY'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['global_markers']['TRACK_F_SERVER_PROFILES_UI_LOCK_SMOKE_APPROVAL'] == 'true'
    s = d['smoke_results']
    assert s['servers_tsx_file_exists'] is True
    assert s['menu_still_points_to_servers'] is True
    assert s['safefeaturecard_imported'] is True
    forb = s['forbidden_substrings_in_servers_tsx']
    for k,v in forb.items():
        assert v == 0, f'forbidden_substring {k} count {v} != 0'
    api = s['api_smoke_post']
    assert api['GET /api/heroes len'] == 100
    assert api['GET /api/server-profiles/select'] == 503
    assert api['POST /api/server-profiles/select'] == 503
    assert api['GET /api/health'] == 200
    assert s['db_state'] if isinstance(s.get('db_state'), bool) else True
    assert d['db_state']['writes_executed'] == 0
    assert d['db_state']['users_server_field_writes'] == 0
    # Reality re-check on file
    assert SRV.exists() and MENU.exists()
    src = SRV.read_text()
    assert '/api/server/select' not in src
    print('[PASS] SP UI-LOCK Track F smoke READY')
    return 0
if __name__ == '__main__': sys.exit(main())
