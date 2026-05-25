#!/usr/bin/env python3
# PROJECT_SERVER_PROFILES_LEGACY_DEPRECATION_AUDIT / TRACK E
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_dual_route_deprecation_plan_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_E_SERVER_PROFILES_DUAL_ROUTE_DEPRECATION_PLAN_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['global_markers']['TRACK_E_SERVER_PROFILES_DUAL_ROUTE_DEPRECATION_PLAN_APPROVAL'] == 'true'
    stages = d['deprecation_stages']
    assert isinstance(stages, list) and len(stages) >= 6
    nums = [s['stage'] for s in stages]
    assert nums == sorted(nums), 'stages must be sequential'
    # Stage 1 is the current audit; IN_PROGRESS
    assert stages[0]['name'].startswith('AUDIT_ONLY')
    assert stages[0]['status'] == 'IN_PROGRESS'
    # All other stages PENDING
    for s in stages[1:]:
        assert s['status'] == 'PENDING', f"stage {s['name']} not PENDING"
    # Every stage has approval marker name
    for s in stages:
        assert s.get('approval_required'), f"stage {s.get('stage')} missing approval_required"
    print(f"[PASS] SP Track E dual-route deprecation plan READY \u2014 stages={len(stages)}")
    return 0
if __name__ == '__main__': sys.exit(main())
