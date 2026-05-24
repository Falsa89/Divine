#!/usr/bin/env python3
# PROJECT_X TRACK A — FRONTEND ROUTE / NAVIGATION INVENTORY VALIDATOR
import json, sys
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_x_frontend_route_inventory_v1.json')
FRONTEND_APP = Path('/app/frontend/app')
TABS_LAYOUT = FRONTEND_APP / '(tabs)/_layout.tsx'

def main():
    if not MARKER.exists():
        print('[FAIL] marker JSON missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_A_FRONTEND_ROUTE_AND_NAVIGATION_INVENTORY_READY'
    assert m['audit_only'] is True
    assert m['frontend_mutation'] is False
    assert m['backend_mutation'] is False
    assert TABS_LAYOUT.exists(), '(tabs)/_layout.tsx missing'
    assert m['tab_routes']['count'] == 5
    # Check actual presence of declared tabs
    layout_text = TABS_LAYOUT.read_text()
    for t in m['tab_routes']['items']:
        name = t['route'].split('/')[-1]
        assert f'name="{name}"' in layout_text, f'tab {name} not in layout'
    # Check existence of root routes
    missing = [r for r in m['root_routes'] if not (FRONTEND_APP / f'{r}.tsx').exists()]
    assert not missing, f'declared root routes missing on disk: {missing}'
    print(f'[PASS] PROJECT_X Track A frontend route inventory READY — tabs={m["tab_routes"]["count"]}, root_routes={len(m["root_routes"])}, menu_voices={m["menu_route_count"]}, dev_admin_screens={len(m["dev_admin_only_routes"])}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
