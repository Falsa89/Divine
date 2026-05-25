#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/frontend/mode_feature_wiring_registry_server_profiles_refresh_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_G_MODE_WIRING_REGISTRY_REFRESH_SERVER_PROFILES_READY'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['frontend_runtime_changes_in_track'] == 0
    assert d['runtime_alteration'] is False
    assert d['global_markers']['TRACK_G_MODE_WIRING_REGISTRY_REFRESH_SERVER_PROFILES_APPROVAL'] == 'true'
    e = d['refreshed_mode_entry']
    assert e['mode_id'] == 'server_profiles'
    assert e['frontend_status'] == 'LOCKED_PREVIEW'
    assert e['backend_status'] == 'FLAG_GATED_503'
    assert e['legacy_player_mutation_surface'] == 'REMOVED'
    assert e['risk_level'] == 'MEDIUM'
    assert e['next_action'] == 'dual_read_preview_then_auth_contract_hardening'
    print('[PASS] DUAL-READ Track G registry refresh READY')
    return 0
if __name__ == '__main__': sys.exit(main())
