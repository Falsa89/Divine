#!/usr/bin/env python3
import json, sys, hashlib
from pathlib import Path
P = Path('/app/data/design/project_management/project_server_profiles_auth_contract_completion_v1.json')
BE = Path('/app/backend/battle_engine.py')
ENV = Path('/app/backend/.env')
SP = Path('/app/backend/routes/server_profiles.py')
ECON = Path('/app/backend/routes/economy.py')
MENU = Path('/app/frontend/app/(tabs)/menu.tsx')
SRV = Path('/app/frontend/app/servers.tsx')
def md5_of(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_H_PROJECT_SERVER_PROFILES_AUTH_CONTRACT_COMPLETION_READY'
    assert d['global_verdict'] == 'PROJECT_SERVER_PROFILES_AUTH_AND_CONTRACT_HARDENING_READY'
    assert d['implementation_mode'] == 'design_only'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['frontend_changes'] == 0
    assert d['flag_flips'] == 0
    # All canonical files MUST remain frozen (design-only pack)
    for hash_key, p in [('battle_engine_md5_post', BE), ('env_md5_post', ENV), ('server_profiles_py_md5_post', SP), ('economy_py_md5_post', ECON), ('menu_md5_post', MENU), ('servers_tsx_md5_post', SRV)]:
        actual = md5_of(p)
        assert actual == d[hash_key], f'{p.name} drift: expected {d[hash_key]} got {actual}'
    # Track verdicts all READY
    for k in 'ABCDEFGH':
        assert k in d['track_verdicts'] and 'READY' in d['track_verdicts'][k]
    # Readiness improved
    assert d['server_profile_wiring_readiness_post'] > d['server_profile_wiring_readiness_pre']
    # Progress max +0.5pp
    diff = d['progress_estimate']['global_project_post'] - d['progress_estimate']['global_project_pre']
    assert 0 <= diff <= 0.5
    assert d['recommended_next_pack_primary']
    print(f"[PASS] AUTH-HARDEN Track H completion \u2014 wiring={d['server_profile_wiring_readiness_post']}%, next={d['recommended_next_pack_primary']}")
    return 0
if __name__ == '__main__': sys.exit(main())
