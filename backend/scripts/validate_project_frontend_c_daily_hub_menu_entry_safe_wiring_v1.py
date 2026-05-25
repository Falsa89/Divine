#!/usr/bin/env python3
import json, sys, hashlib
from pathlib import Path
M = Path('/app/data/design/frontend/project_frontend_c_daily_hub_menu_entry_safe_wiring_v1.json')
MENU = Path('/app/frontend/app/(tabs)/menu.tsx')
TABS_LAYOUT = Path('/app/frontend/app/(tabs)/_layout.tsx')
def main():
    m = json.loads(M.read_text())
    assert m['verdict'] == 'TRACK_D_DAILY_HUB_MENU_ENTRY_SAFE_WIRING_READY'
    assert m['new_bottom_tab'] is False
    assert m['broad_navigation_refactor'] is False
    assert m['_layout_tabs_modified'] is False
    assert m['voices_added_count'] == 1
    # Verify menu file actually has the entry
    menu_text = MENU.read_text()
    assert '/daily-hub' in menu_text, 'menu does not link to /daily-hub'
    assert 'Guida Giornaliera' in menu_text
    # tab layout invariato (5 tabs)
    layout_text = TABS_LAYOUT.read_text()
    assert layout_text.count('<Tabs.Screen') == 5
    print('[PASS] FC Track D menu wiring READY — voices_added=1, new_tab=0, broad_refactor=0')
    return 0
if __name__ == '__main__': sys.exit(main())
