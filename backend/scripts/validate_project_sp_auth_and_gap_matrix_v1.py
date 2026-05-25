#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_auth_and_gap_matrix_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_D_SERVER_PROFILES_AUTH_AND_GAP_MATRIX_READY'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['global_markers']['TRACK_D_SERVER_PROFILES_AUTH_AND_GAP_MATRIX_APPROVAL'] == 'true'
    gm = d['gap_matrix']
    assert isinstance(gm, list) and len(gm) >= 6
    # Must contain at least one CRITICAL (orphan/seed)
    sevs = [g['severity'] for g in gm]
    assert sevs.count('CRITICAL') >= 1
    # auth gap must be present
    assert any('auth' in g['gap'].lower() for g in gm)
    # seed gap must be present
    assert any('seed' in g['gap'].lower() for g in gm)
    assert d['flag_flip_authorized'] is False
    assert d['blocker_count_for_flag_flip'] >= 4
    print(f"[PASS] DUAL-READ Track D auth/gap matrix READY \u2014 gaps={len(gm)}, critical={sevs.count('CRITICAL')}")
    return 0
if __name__ == '__main__': sys.exit(main())
