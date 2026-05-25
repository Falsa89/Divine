#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_dual_read_preview_smoke_no_mutation_guard_v1.json')
FE_APP = Path('/app/frontend/app')
FE_COMP = Path('/app/frontend/components')
FE_UTILS = Path('/app/frontend/utils')
FORBIDDEN = ['/api/server/select', 'selectServer', 'select_server', 'Server Selezionato']
def scan_dir(d):
    hits = []
    if not d.exists(): return hits
    for f in d.rglob('*'):
        if f.is_file() and f.suffix in ('.ts','.tsx','.js','.jsx'):
            try: txt = f.read_text(errors='ignore')
            except Exception: continue
            for pat in FORBIDDEN:
                if pat in txt: hits.append((str(f), pat))
    return hits
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_F_DUAL_READ_PREVIEW_SMOKE_AND_NO_MUTATION_GUARD_READY'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['global_markers']['TRACK_F_DUAL_READ_PREVIEW_SMOKE_NO_MUTATION_GUARD_APPROVAL'] == 'true'
    s = d['smoke']
    assert s['frontend_post_server_select_count'] == 0
    assert s['frontend_legacy_server_select_substring_count'] == 0
    assert s['servers_route_still_locked'] is True
    assert s['select_button_count_in_servers_tsx'] == 0
    api = s['api_smoke']
    assert api['GET /api/heroes len'] == 100
    assert api['GET /api/server-profiles/select'] == 503
    assert api['POST /api/server-profiles/select'] == 503
    assert api['GET /api/health'] == 200
    db = s['db_state']
    assert db['users_server_writes_during_smoke'] == 0
    assert db['server_profiles_writes_during_smoke'] == 0
    # Live regression scan: zero forbidden substrings in player UI
    hits = scan_dir(FE_APP) + scan_dir(FE_COMP) + scan_dir(FE_UTILS)
    assert len(hits) == 0, f'forbidden substrings found: {hits}'
    print(f'[PASS] DUAL-READ Track F smoke/no-mutation guard READY \u2014 forbidden_hits=0')
    return 0
if __name__ == '__main__': sys.exit(main())
