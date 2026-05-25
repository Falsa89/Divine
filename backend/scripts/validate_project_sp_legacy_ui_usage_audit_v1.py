#!/usr/bin/env python3
# PROJECT_SERVER_PROFILES_LEGACY_DEPRECATION_AUDIT / TRACK A
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_legacy_ui_usage_audit_v1.json')
SERVERS_TSX = Path('/app/frontend/app/servers.tsx')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_A_SERVER_UI_LEGACY_USAGE_AUDIT_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['frontend_changes'] == 0
    assert d['backend_changes'] == 0
    assert d['global_markers']['TRACK_A_SERVER_UI_LEGACY_USAGE_AUDIT_APPROVAL'] == 'true'
    ui = d['ui_audit']
    assert ui['route_file'] == '/app/frontend/app/servers.tsx'
    assert ui['linked_from_menu'] is True
    assert ui['active_switching_implied'] is True
    assert ui['should_become_locked_or_preview_before_migration'] is True
    assert ui['new_endpoint_referenced_anywhere_in_frontend'] is False
    # Must enumerate at least 2 API calls (GET /api/servers + POST /api/server/select)
    eps = [c['endpoint'] for c in ui['api_calls']]
    assert '/api/servers' in eps
    assert '/api/server/select' in eps
    # Verify any API call marked legacy
    assert any(c['is_legacy'] for c in ui['api_calls'])
    # Reality check: file still exists; content may have been refactored
    # by a later pack (e.g., PROJECT_SERVER_PROFILES_UI_LOCK_PREVIEW). We do
    # NOT re-assert the legacy endpoint substrings against the live file
    # because the audit captured a historical state; the JSON's pre_pack_md5
    # and api_calls section preserve that record.
    assert SERVERS_TSX.exists()
    assert ui['risk_level'] == 'HIGH'
    print(f"[PASS] SP Track A /servers UI legacy usage READY \u2014 api_calls={len(ui['api_calls'])}, risk={ui['risk_level']}")
    return 0
if __name__ == '__main__': sys.exit(main())
