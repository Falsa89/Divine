#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_auth_surface_audit_v1.json')
SRV = Path('/app/backend/server.py')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_A_SERVER_PROFILE_AUTH_SURFACE_AUDIT_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0 and d['backend_changes'] == 0
    assert d['global_markers']['TRACK_A_SERVER_PROFILE_AUTH_SURFACE_AUDIT_APPROVAL'] == 'true'
    a = d['auth_surface']
    assert 'get_current_user' in a['primary_helper']
    assert a['scheme'].startswith('JWT Bearer')
    assert a['algorithm'] == 'HS256'
    # Reality check: get_current_user actually exists in server.py
    src = SRV.read_text()
    assert 'async def get_current_user' in src
    assert 'JWT_SECRET' in src
    gaps = d['gaps_identified']
    assert any(g.get('blocker_for_flag_flip') is True for g in gaps), 'must identify at least 1 blocker'
    assert d['flag_flip_authorized'] is False
    print(f"[PASS] AUTH-HARDEN Track A auth surface audit READY \u2014 gaps={len(gaps)}")
    return 0
if __name__ == '__main__': sys.exit(main())
