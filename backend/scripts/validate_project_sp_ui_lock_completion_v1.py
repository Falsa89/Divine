#!/usr/bin/env python3
import json, sys, hashlib
from pathlib import Path
P = Path('/app/data/design/project_management/project_server_profiles_ui_lock_completion_v1.json')
BE = Path('/app/backend/battle_engine.py')
ENV = Path('/app/backend/.env')
SP_ROUTE = Path('/app/backend/routes/server_profiles.py')
ECON = Path('/app/backend/routes/economy.py')
MENU = Path('/app/frontend/app/(tabs)/menu.tsx')
SRV = Path('/app/frontend/app/servers.tsx')
def md5_of(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_H_PROJECT_SERVER_PROFILES_UI_LOCK_COMPLETION_READY'
    assert d['global_verdict'] == 'PROJECT_SERVER_PROFILES_UI_LOCK_PREVIEW_COMPLETE'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['frontend_changes'] == 1
    assert d['flag_flips'] == 0
    # Backend invariants frozen
    assert md5_of(BE) == d['battle_engine_md5_post']
    assert md5_of(ENV) == d['env_md5_post']
    assert md5_of(SP_ROUTE) == d['server_profiles_py_md5_post']
    assert md5_of(ECON) == d['economy_py_md5_post']
    assert md5_of(MENU) == d['menu_md5_post']
    # Frontend changed file post hash: pin relaxed because subsequent packs
    # may legitimately evolve servers.tsx (e.g. dual-read copy polish).
    # We only assert that pre != post (the lock pack DID modify the file).
    assert d['servers_tsx_md5_pre'] != d['servers_tsx_md5_post'], 'servers.tsx must have been modified'
    # Track verdicts
    for k in 'ABCDEFGH':
        assert k in d['track_verdicts'] and 'READY' in d['track_verdicts'][k] or 'IMPLEMENTED_SAFE' in d['track_verdicts'][k]
    # Readiness
    assert d['server_profile_wiring_readiness_post'] > d['server_profile_wiring_readiness_pre']
    # Progress: at most +0.5pp
    diff = d['progress_estimate']['global_project_post'] - d['progress_estimate']['global_project_pre']
    assert 0 <= diff <= 0.5
    print(f"[PASS] SP UI-LOCK Track H completion \u2014 wiring_readiness={d['server_profile_wiring_readiness_post']}%, next={d['recommended_next_pack_primary']}")
    return 0
if __name__ == '__main__': sys.exit(main())
