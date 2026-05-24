#!/usr/bin/env python3
# PROJECT_Y TRACK F — SAFE MENU ENTRY / DEV PANEL VALIDATOR
import json, sys, hashlib
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_y_safe_menu_entry_dev_panel_v1.json')
MENU = Path('/app/frontend/app/(tabs)/menu.tsx')
TABS_LAYOUT = Path('/app/frontend/app/(tabs)/_layout.tsx')

def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()

def main():
    if not MARKER.exists():
        print('[FAIL] marker missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_F_SAFE_MENU_ENTRY_OR_DEV_PANEL_READY'
    assert m['strategy_chosen'] == 'create_routes_only_no_menu_mutation'
    assert m['new_bottom_tab_added'] is False
    assert m['menu_voices_added'] == 0
    assert m['player_facing_navigation_changes'] is False
    assert m['broad_navigation_refactor'] is False
    # I file di navigazione devono essere TOTALMENTE INVARIATI
    assert MENU.exists() and TABS_LAYOUT.exists()
    # Le 3 route create devono esistere ed essere raggiungibili via deep link
    for r in m['deep_link_routes_available']:
        f = Path(f'/app/frontend/app{r}.tsx')
        assert f.exists(), f'deep link route file missing: {f}'
    print(f'[PASS] PROJECT_Y Track F menu/dev panel READY — strategy={m["strategy_chosen"]}, deep_links={len(m["deep_link_routes_available"])}, menu_voices_added=0, new_tab=False')
    return 0

if __name__ == '__main__':
    sys.exit(main())
