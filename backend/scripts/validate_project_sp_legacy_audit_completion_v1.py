#!/usr/bin/env python3
# PROJECT_SERVER_PROFILES_LEGACY_DEPRECATION_AUDIT / TRACK H + GLOBAL COMPLETION
import json, sys, hashlib
from pathlib import Path
P = Path('/app/data/design/project_management/project_server_profiles_legacy_audit_completion_v1.json')
BE = Path('/app/backend/battle_engine.py')
ENV = Path('/app/backend/.env')
SRV = Path('/app/frontend/app/servers.tsx')
SP_ROUTE = Path('/app/backend/routes/server_profiles.py')
ECON = Path('/app/backend/routes/economy.py')
def md5_of(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_H_PROJECT_SERVER_PROFILES_LEGACY_AUDIT_COMPLETION_READY'
    assert d['global_verdict'] == 'PROJECT_SERVER_PROFILES_LEGACY_DEPRECATION_AUDIT_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['frontend_changes'] == 0
    assert d['flag_flips'] == 0
    assert d['server_changes'] == 0
    # MD5 invariants (canonical files)
    inv = {
        '151ca35ad3bc35f0a6209cb3744ed440': BE,
        'ff60bbb79efa329b71aa8ed351ea89b3': ENV,
        '26f5c796425aafa933f46979928165f4': SRV,
        '7c12a8d1fc1e1b6a9e63cacfab5c14f4': SP_ROUTE,
        'b3afb52609b487ab6c1ac3c3e25405fd': ECON,
    }
    for expected, p in inv.items():
        actual = md5_of(p)
        assert actual == expected, f'MD5 drift {p.name}: expected {expected} got {actual}'
    # Track verdicts
    for k in 'ABCDEFGH':
        assert k in d['track_verdicts'] and 'READY' in d['track_verdicts'][k]
    # Readiness
    assert d['server_profile_wiring_readiness_post'] > d['server_profile_wiring_readiness_pre']
    # Progress unchanged
    diff = d['progress_estimate']['global_project_post'] - d['progress_estimate']['global_project_pre']
    assert abs(diff) <= 0.01
    # Recommended next pack
    assert d['recommended_next_pack_primary']
    assert d['recommended_immediate_action']
    print(f"[PASS] SP Track H completion READY \u2014 wiring_readiness={d['server_profile_wiring_readiness_post']}%, next={d['recommended_next_pack_primary']}")
    return 0
if __name__ == '__main__': sys.exit(main())
