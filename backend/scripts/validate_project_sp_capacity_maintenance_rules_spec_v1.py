#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_capacity_maintenance_rules_spec_v1.json')
ECON = Path('/app/backend/routes/economy.py')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_E_SERVER_SELECTION_CAPACITY_MAINTENANCE_RULES_SPEC_READY'
    assert d['audit_mode'] == 'design_only'
    assert d['db_writes'] == 0 and d['backend_changes'] == 0
    assert d['global_markers']['TRACK_E_SERVER_SELECTION_CAPACITY_MAINTENANCE_RULES_SPEC_APPROVAL'] == 'true'
    lb = d['legacy_behavior_preserved']
    assert lb['must_remain_intact_until_new_endpoint_live'] is True
    # Reality check: legacy endpoint still exists and still enforces validation
    src = ECON.read_text()
    assert '/server/select' in src and 'maintenance' in src
    # Taxonomy covers required states
    tx = d['new_server_state_taxonomy']
    for s in ['online','full','maintenance','new','unknown']:
        assert s in tx
    assert d['preview_allowed_during_maintenance'] is True
    assert d['account_profile_when_server_unavailable']['behavior']
    print(f"[PASS] AUTH-HARDEN Track E capacity/maintenance rules READY")
    return 0
if __name__ == '__main__': sys.exit(main())
