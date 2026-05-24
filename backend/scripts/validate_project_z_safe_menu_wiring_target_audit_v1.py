#!/usr/bin/env python3
# PROJECT_Z TRACK A — SAFE MENU WIRING TARGET AUDIT VALIDATOR
import json, sys
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_z_safe_menu_wiring_target_audit_v1.json')
VALID_STRATEGIES = {
    'existing_dev_admin_panel', 'existing_menu_section_locked_label_each_route',
    'dedicated_safe_preview_hub_single_menu_entry', 'no_menu_wiring_keep_deep_link_only',
}
VALID_VERDICTS = {
    'TRACK_A_SAFE_MENU_WIRING_TARGET_AUDIT_READY',
    'TRACK_A_MENU_WIRING_UNSAFE_DEFERRED',
}
def main():
    if not MARKER.exists():
        print('[FAIL] marker missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] in VALID_VERDICTS
    assert m['audit_only'] is True
    assert m['broad_navigation_refactor'] is False
    assert m['new_bottom_tab'] is False
    assert m['selected_strategy'] in VALID_STRATEGIES
    assert len(m['options_evaluated']) >= 3
    print(f'[PASS] PROJECT_Z Track A menu wiring audit READY — strategy={m["selected_strategy"]}, options_evaluated={len(m["options_evaluated"])}')
    return 0
if __name__ == '__main__':
    sys.exit(main())
