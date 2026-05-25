#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_legacy_current_server_read_model_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_B_LEGACY_CURRENT_SERVER_READ_MODEL_READY'
    assert d['audit_mode'] == 'design_only'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['frontend_changes_in_track'] == 0
    assert d['global_markers']['TRACK_B_LEGACY_CURRENT_SERVER_READ_MODEL_APPROVAL'] == 'true'
    m = d['model']
    assert m['read_source_primary'] == 'users.server (string)'
    assert m['active_switching'] is False
    assert m['write_back'] is False
    assert 'fallback_when_user_has_no_server' in m
    assert isinstance(m['avoiding_divergence_with_server_profiles'], list) and len(m['avoiding_divergence_with_server_profiles']) >= 3
    forb = d['forbidden_actions']
    for f in ['users write', 'migration', 'server_profiles write']:
        assert f in forb
    print('[PASS] DUAL-READ Track B legacy current-server read model READY')
    return 0
if __name__ == '__main__': sys.exit(main())
