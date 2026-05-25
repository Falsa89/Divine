#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_pre_home_server_selection_ux_requirement_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_C_PRE_HOME_SERVER_SELECTION_UX_REQUIREMENT_READY'
    assert d['audit_mode'] == 'requirement_only'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['frontend_changes'] == 0
    assert d['global_markers']['TRACK_C_PRE_HOME_SERVER_SELECTION_UX_REQUIREMENT_APPROVAL'] == 'true'
    flow = d['future_flow']
    assert flow == ['AccountLogin', 'PreHomeServerSelection', 'Home']
    sec = d['sections_required']
    ids = [s['id'] for s in sec]
    for required in ['last_used','recent','available','new']:
        assert required in ids, f'missing section {required}'
    # Server state visual legend covers required states
    legend = d['server_state_visual_legend']
    for s in ['online','full','maintenance','new']:
        assert s in legend
    # Fallbacks cover documented scenarios
    fb = d['fallbacks']
    for k in ['one_server_only','no_server_profile_yet','all_servers_in_maintenance','server_profiles_call_503']:
        assert k in fb, f'missing fallback {k}'
    # Relationship with internal /servers preview captured
    rel = d['relationship_with_internal_preview']
    assert rel['internal_preview_route'].startswith('/servers')
    assert rel['future_pre_home_route'].startswith('/login-server-select')
    print(f"[PASS] AUTH-HARDEN Track C pre-home UX requirement READY \u2014 sections={len(sec)}, fallbacks={len(fb)}")
    return 0
if __name__ == '__main__': sys.exit(main())
