#!/usr/bin/env python3
import json, sys, hashlib
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_no_mutation_regression_guard_v1.json')
FE_APP = Path('/app/frontend/app')
FE_COMP = Path('/app/frontend/components')
FE_UTILS = Path('/app/frontend/utils')
MENU = Path('/app/frontend/app/(tabs)/menu.tsx')
FORB = ['/api/server/select','selectServer','select_server','Server Selezionato']
def scan(d):
    hits = []
    if not d.exists(): return hits
    for f in d.rglob('*'):
        if f.is_file() and f.suffix in ('.ts','.tsx','.js','.jsx'):
            try: txt = f.read_text(errors='ignore')
            except Exception: continue
            for pat in FORB:
                if pat in txt: hits.append((str(f), pat))
    return hits
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_F_SERVER_PROFILES_NO_MUTATION_REGRESSION_GUARD_READY'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['global_markers']['TRACK_F_SERVER_PROFILES_NO_MUTATION_REGRESSION_GUARD_APPROVAL'] == 'true'
    chk = d['checks']
    assert chk['frontend_post_server_select_count'] == 0
    assert chk['servers_route_still_locked'] is True
    assert chk['api_server_profiles_select_get'] == 503
    assert chk['api_server_profiles_select_post'] == 503
    # Live scan
    hits = scan(FE_APP) + scan(FE_COMP) + scan(FE_UTILS)
    assert len(hits) == 0, f'forbidden hits: {hits}'
    # Menu MD5 stable
    actual_menu_md5 = hashlib.md5(MENU.read_bytes()).hexdigest()
    assert actual_menu_md5 == chk['menu_md5_unchanged'], f'menu drift: {actual_menu_md5}'
    print(f"[PASS] AUTH-HARDEN Track F no-mutation regression guard READY \u2014 hits=0")
    return 0
if __name__ == '__main__': sys.exit(main())
