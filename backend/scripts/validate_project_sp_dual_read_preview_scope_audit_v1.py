#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_dual_read_preview_scope_audit_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_A_DUAL_READ_PREVIEW_SCOPE_AUDIT_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['frontend_changes_in_track'] == 0
    assert d['flag_flips'] == 0
    assert d['global_markers']['TRACK_A_DUAL_READ_PREVIEW_SCOPE_AUDIT_APPROVAL'] == 'true'
    s = d['scope']
    assert s['can_legacy_users_server_be_displayed_in_locked_preview'] is True
    assert s['server_profiles_count_zero_blocks_live_preview'] is True
    assert s['server_profiles_count_zero_blocks_dual_read_preview'] is False
    assert isinstance(s['why_mutation_remains_blocked'], list) and len(s['why_mutation_remains_blocked']) >= 4
    assert isinstance(s['remaining_before_auth_contract_hardening'], list) and len(s['remaining_before_auth_contract_hardening']) >= 3
    assert s['endpoint_helper_needed_later']['name'].startswith('GET /api/account/server-profiles/preview')
    print('[PASS] DUAL-READ Track A scope audit READY')
    return 0
if __name__ == '__main__': sys.exit(main())
