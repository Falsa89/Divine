#!/usr/bin/env python3
import json, sys
from pathlib import Path
M = Path('/app/data/design/frontend/project_frontend_c_daily_hub_mobile_accessibility_polish_v1.json')
ROUTE = Path('/app/frontend/app/daily-hub.tsx')
def main():
    m = json.loads(M.read_text())
    assert m['verdict'] == 'TRACK_F_DAILY_HUB_MOBILE_ACCESSIBILITY_POLISH_READY'
    text = ROUTE.read_text()
    assert 'SafeAreaView' in text
    assert 'accessibilityLabel' in text
    assert 'accessibilityRole' in text
    assert 'accessibilityHint' in text
    p = m['mobile_polish']
    assert p['safe_area_view_used'] is True
    a = m['accessibility']
    assert a['back_button_accessibilityLabel'] is True
    assert a['entry_card_accessibilityRole_link'] is True
    print('[PASS] FC Track F mobile/accessibility READY — SafeArea=True, all_a11y_props=True')
    return 0
if __name__ == '__main__': sys.exit(main())
