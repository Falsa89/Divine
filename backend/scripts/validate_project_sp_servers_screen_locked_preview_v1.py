#!/usr/bin/env python3
import json, sys, hashlib
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_servers_screen_locked_preview_v1.json')
SRV = Path('/app/frontend/app/servers.tsx')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_B_SERVERS_SCREEN_LOCKED_PREVIEW_IMPLEMENTED_SAFE'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['frontend_changes'] == 1
    assert d['flag_flips'] == 0
    assert d['global_markers']['TRACK_B_SERVERS_SCREEN_LOCKED_PREVIEW_IMPLEMENTATION_APPROVAL'] == 'true'
    assert SRV.exists()
    src = SRV.read_text()
    # Anti-leak: legacy mutation surface must be GONE
    assert '/api/server/select' not in src, 'legacy /api/server/select still referenced in servers.tsx'
    assert 'Server Selezionato' not in src, 'legacy success copy still present'
    assert 'selectServer' not in src
    assert 'select_server' not in src
    # SafeFeatureCard must be imported
    assert 'SafeFeatureCard' in src
    # Italian locked copy must be present
    assert 'Selezione Server in aggiornamento' in src
    assert 'in fase di migrazione' in src
    # Read-only GET /api/servers usage was intentionally REMOVED in the
    # final lock pass to align with audit_server_selection_runtime_safety_v1
    # which forbids any UI fetch of /api/servers. The locked preview now
    # shows only the banner + new-endpoint state card + footer.
    assert '/api/servers' not in src, 'legacy /api/servers fetch must NOT be present in locked preview'
    # Verify MD5 matches recorded post-pack hash
    md5 = hashlib.md5(SRV.read_bytes()).hexdigest()
    assert md5 == d['post_pack_md5'], f'servers.tsx MD5 drift: expected {d["post_pack_md5"]} got {md5}'
    chk = d['requirements_check']
    for k in ['no_enabled_server_select_button','no_post_server_select_call','no_success_alert_implying_switching','safefeaturecard_pattern_used','menu_entry_kept_unchanged']:
        assert chk[k] is True, f'requirement {k} not true'
    print(f'[PASS] SP UI-LOCK Track B servers screen locked preview implemented \u2014 md5={md5[:8]}')
    return 0
if __name__ == '__main__': sys.exit(main())
