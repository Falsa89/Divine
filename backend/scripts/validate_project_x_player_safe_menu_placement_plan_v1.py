#!/usr/bin/env python3
# PROJECT_X TRACK C — PLAYER SAFE MENU PLACEMENT PLAN VALIDATOR
import json, sys
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_x_player_safe_menu_placement_plan_v1.json')

def main():
    if not MARKER.exists():
        print('[FAIL] marker JSON missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_C_PLAYER_SAFE_MENU_PLACEMENT_PLAN_READY'
    assert m['audit_only'] is True
    assert m['ui_implementation'] is False
    assert m['home_button_visibility']['add_new_player_facing_buttons'] is False
    assert m['bottom_nav_rules']['add_new_tab'] is False
    assert m['bottom_nav_rules']['keep_existing_5_tabs'] is True
    assert m['dead_button_policy']['locked_cards_must_be_non_actionable'] is True
    assert m['dead_button_policy']['never_route_to_503_endpoint_call'] is True
    recs = m['main_menu_hub_recommendations']
    assert len(recs) >= 5
    classes = {r['visibility'] for r in recs}
    assert classes.issubset({'player_visible_locked', 'player_visible_active', 'dev_admin_only'})
    print(f'[PASS] PROJECT_X Track C menu placement plan READY — recommendations={len(recs)}, locked={len(m["player_visible_locked_cards"])}, dev_admin_screens={len(m["dev_admin_only_section"]["existing_screens"])+len(m["dev_admin_only_section"]["future_screens"])}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
