#!/usr/bin/env python3
# PROJECT_SERVER_PROFILES_LEGACY_DEPRECATION_AUDIT / TRACK B
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_legacy_endpoint_behavior_audit_v1.json')
ECON = Path('/app/backend/routes/economy.py')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_B_LEGACY_SERVER_ENDPOINT_BEHAVIOR_AUDIT_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['global_markers']['TRACK_B_LEGACY_SERVER_ENDPOINT_BEHAVIOR_AUDIT_APPROVAL'] == 'true'
    eps = {e['endpoint']: e for e in d['endpoints']}
    assert 'GET /api/servers' in eps
    assert 'POST /api/server/select' in eps
    post = eps['POST /api/server/select']
    assert post['mutates_active_server_state'] is True
    writes_joined = ' '.join(post['writes'])
    assert 'users' in writes_joined and 'update_one' in writes_joined
    assert post['auth_required'] is True
    assert 'DEPRECATED' in post['deprecation_note']
    # Reality check
    src = ECON.read_text()
    assert 'users.update_one' in src
    assert '/server/select' in src
    assert d['risk_level'] == 'HIGH'
    print(f"[PASS] SP Track B legacy endpoint behavior READY \u2014 endpoints={len(eps)}, risk={d['risk_level']}")
    return 0
if __name__ == '__main__': sys.exit(main())
