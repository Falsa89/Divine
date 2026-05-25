#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/frontend/mode_feature_wiring_registry_server_profiles_update_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_G_MODE_WIRING_REGISTRY_UPDATE_FOR_SERVER_PROFILES_READY'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['frontend_runtime_changes_in_this_track'] == 0
    assert d['global_markers']['TRACK_G_MODE_WIRING_REGISTRY_UPDATE_SERVER_PROFILES_APPROVAL'] == 'true'
    u = d['server_profiles_mode_update']
    assert u['mode_id'] == 'server_profiles'
    assert u['prev_frontend_status'] == 'WIRED'
    assert u['new_frontend_status'] == 'LOCKED_PREVIEW'
    assert u['prev_risk_level'] == 'HIGH'
    assert u['new_risk_level'] in ('LOW','MEDIUM')
    assert u['player_facing_legacy_mutation_removed_from_ui_surface'] is True
    assert d['high_risk_count_post'] < d['high_risk_count_pre']
    print(f"[PASS] SP UI-LOCK Track G registry update READY \u2014 high_risks {d['high_risk_count_pre']} \u2192 {d['high_risk_count_post']}")
    return 0
if __name__ == '__main__': sys.exit(main())
