#!/usr/bin/env python3
# PROJECT_Z TRACK G — EXPO GO MOBILE QA SMOKE VALIDATOR
import json, sys
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_z_expo_go_mobile_qa_smoke_v1.json')
VALID_VERDICTS = {
    'TRACK_G_EXPO_GO_MOBILE_QA_SMOKE_READY',
    'TRACK_G_MOBILE_SCREENSHOT_MANUAL_PENDING',
}

def main():
    if not MARKER.exists():
        print('[FAIL] marker missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] in VALID_VERDICTS
    assert m['fake_screenshot_verification'] is False
    static = m['static_smoke_run']
    assert static['route_compile_check'] == 'PASS'
    assert static['safefeaturecard_imported_in_all_4_routes'] is True
    assert 'PASS' in static['forbidden_labels_scan']
    assert 'PASS' in static['mutating_api_calls_scan']
    assert m['automation_status']['bundle_metro_compiles_clean'] is True
    if m['verdict'] == 'TRACK_G_MOBILE_SCREENSHOT_MANUAL_PENDING':
        assert len(m['manual_qa_checklist']) >= 8
        assert m['verdict_status'] == 'MANUAL_DEVICE_SCREENSHOT_PENDING'
    print(f'[PASS] PROJECT_Z Track G expo go QA smoke — verdict={m["verdict"]}, static_smoke=PASS, manual_checks={len(m["manual_qa_checklist"])}, fake_screenshot=False')
    return 0
if __name__ == '__main__':
    sys.exit(main())
