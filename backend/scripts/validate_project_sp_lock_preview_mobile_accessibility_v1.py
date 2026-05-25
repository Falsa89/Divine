#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_lock_preview_mobile_accessibility_v1.json')
SRV = Path('/app/frontend/app/servers.tsx')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_E_SERVER_LOCK_PREVIEW_MOBILE_ACCESSIBILITY_READY'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    assert d['global_markers']['TRACK_E_SERVER_LOCK_PREVIEW_MOBILE_ACCESSIBILITY_APPROVAL'] == 'true'
    c = d['checks']
    assert c['safe_area_used'] is True
    assert c['scrollview_used'] is True
    assert c['accessibility_state_disabled_on_rows'] is True
    assert c['no_touchable_for_server_selection'] is True
    assert c['no_fake_mobile_screenshot_verification'] is True
    # Reality check
    src = SRV.read_text()
    assert 'SafeAreaView' in src
    assert 'ScrollView' in src
    assert 'accessibilityLabel' in src
    assert 'accessibilityState' in src
    print('[PASS] SP UI-LOCK Track E mobile/accessibility READY')
    return 0
if __name__ == '__main__': sys.exit(main())
