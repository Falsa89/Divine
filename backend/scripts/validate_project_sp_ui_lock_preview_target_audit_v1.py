#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_ui_lock_preview_target_audit_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_A_SERVER_LOCK_PREVIEW_TARGET_AUDIT_READY'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['global_markers']['TRACK_A_SERVER_LOCK_PREVIEW_TARGET_AUDIT_APPROVAL'] == 'true'
    t = d['target']
    assert t['route_file'] == '/app/frontend/app/servers.tsx'
    assert t['mutation_call_to_remove']
    assert t['safefeaturecard_reusable'] is True
    assert t['menu_entry_should_remain'] is True
    print('[PASS] SP UI-LOCK Track A target audit READY')
    return 0
if __name__ == '__main__': sys.exit(main())
