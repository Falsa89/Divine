#!/usr/bin/env python3
# PROJECT_SERVER_PROFILES_LEGACY_DEPRECATION_AUDIT / TRACK C
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_new_route_contract_audit_v1.json')
ROUTE = Path('/app/backend/routes/server_profiles.py')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_C_NEW_SERVER_PROFILES_ROUTE_CONTRACT_AUDIT_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['global_markers']['TRACK_C_NEW_SERVER_PROFILES_ROUTE_CONTRACT_AUDIT_APPROVAL'] == 'true'
    c = d['contract']
    assert c['prefix'] == '/api/server-profiles'
    eps = {e['endpoint']: e for e in c['endpoints']}
    assert 'GET /api/server-profiles/select' in eps
    assert 'POST /api/server-profiles/select' in eps
    for ep in eps.values():
        assert ep['mutation_capability'] is False
    flags = c['feature_flags']
    assert 'SERVER_PROFILES_RUNTIME_ENABLED' in flags['primary']
    assert 'SERVER_PROFILES_PREVIEW_ENABLED' in flags['secondary']
    # Reality check: route file present and has the flag constant
    src = ROUTE.read_text()
    assert 'SERVER_PROFILES_RUNTIME_ENABLED' in src
    assert 'SERVER_PROFILES_PREVIEW_ENABLED' in src
    assert d['risk_level'] == 'LOW'
    print(f"[PASS] SP Track C new route contract READY \u2014 endpoints={len(eps)}, flag={flags['primary'].split(' ')[0]}")
    return 0
if __name__ == '__main__': sys.exit(main())
