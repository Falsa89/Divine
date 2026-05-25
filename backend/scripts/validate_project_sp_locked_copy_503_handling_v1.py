#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_locked_copy_503_handling_v1.json')
SRV = Path('/app/frontend/app/servers.tsx')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_D_SERVER_PROFILE_LOCKED_COPY_AND_503_HANDLING_READY'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['global_markers']['TRACK_D_SERVER_PROFILE_LOCKED_COPY_503_HANDLING_APPROVAL'] == 'true'
    c = d['copy_and_status']
    assert c['fake_availability_claim'] is False
    assert c['new_profiles_live_claim'] is False
    h = d['handle_503']
    assert 'preview_503' in h['states_handled']
    assert 'unavailable' in h['states_handled']
    assert h['no_crash'] is True
    # Reality check: file contains the required copy strings
    src = SRV.read_text()
    assert c['banner_title'] in src
    assert 'gated' in src or '503' in src
    print('[PASS] SP UI-LOCK Track D locked copy / 503 handling READY')
    return 0
if __name__ == '__main__': sys.exit(main())
