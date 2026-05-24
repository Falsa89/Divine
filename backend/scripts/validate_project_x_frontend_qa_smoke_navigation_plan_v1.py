#!/usr/bin/env python3
# PROJECT_X TRACK G — FRONTEND QA SMOKE NAVIGATION PLAN VALIDATOR
import json, sys
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_x_frontend_qa_smoke_navigation_plan_v1.json')
REQUIRED_SECTIONS = {
    'mobile_first_checks', 'expo_go_checks', 'route_existence_checks',
    'dead_button_checks', 'accidental_live_action_checks',
    'blocked_endpoint_crash_checks', 'empty_error_states', 'smoke_navigation_paths',
}

def main():
    if not MARKER.exists():
        print('[FAIL] marker JSON missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_G_FRONTEND_QA_SMOKE_NAVIGATION_PLAN_READY'
    assert m['audit_only'] is True
    assert m['qa_runtime_automation_with_creds'] is False
    plan = m['qa_plan']
    missing = REQUIRED_SECTIONS - set(plan.keys())
    assert not missing, f'qa_plan missing sections: {missing}'
    for sec, items in plan.items():
        assert isinstance(items, list) and len(items) >= 3, f'section {sec} too short'
    assert m['future_automation']['requires_credentials'] is False
    assert m['future_automation']['runs_in_dev_only'] is True
    total_checks = sum(len(v) for v in plan.values())
    print(f'[PASS] PROJECT_X Track G QA smoke plan READY — sections={len(plan)}, total_checks={total_checks}, smoke_paths={len(plan["smoke_navigation_paths"])}, no_creds=True')
    return 0

if __name__ == '__main__':
    sys.exit(main())
