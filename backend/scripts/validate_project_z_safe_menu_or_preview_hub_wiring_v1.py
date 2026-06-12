#!/usr/bin/env python3
# PROJECT_Z TRACK B — SAFE MENU OR PREVIEW HUB WIRING VALIDATOR
import json, sys, re
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_z_safe_menu_or_preview_hub_wiring_v1.json')
HUB = Path('/app/frontend/app/safe-previews.tsx')
MENU = Path('/app/frontend/app/(tabs)/menu.tsx')
TABS_LAYOUT = Path('/app/frontend/app/(tabs)/_layout.tsx')
VALID_VERDICTS = {
    'TRACK_B_SAFE_MENU_OR_PREVIEW_HUB_WIRED_SAFE',
    'TRACK_B_READY_MENU_WIRING_DEFERRED',
}
FORBIDDEN_HUB_TOKENS = [r'\bEvoca ora\b', r'\bImporta ora\b', r'\bAttiva bonus\b', r'\bCambia server\b', r'\bLancia rollout\b', r'\bSpendi\b']
FORBIDDEN_HUB_API = [r'/api/gacha/pull', r'/api/artifacts/pull', r'/api/server/select', r'/api/affinity/gift-spend']

def main():
    if not MARKER.exists():
        print('[FAIL] marker missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] in VALID_VERDICTS
    assert m['new_bottom_tab_added'] is False
    assert m['broad_navigation_refactor'] is False
    assert m['live_action_label_in_menu'] is False
    if m['verdict'] == 'TRACK_B_SAFE_MENU_OR_PREVIEW_HUB_WIRED_SAFE':
        assert HUB.exists(), 'hub safe-previews.tsx missing'
        hub_text = HUB.read_text()
        assert 'SafeFeatureCard' in hub_text
        for pat in FORBIDDEN_HUB_TOKENS:
            assert not re.search(pat, hub_text, flags=re.IGNORECASE), f'hub forbidden token: {pat}'
        for pat in FORBIDDEN_HUB_API:
            assert not re.search(pat, hub_text), f'hub forbidden api: {pat}'
        # _layout (tabs) NON deve essere stato modificato (no nuove tab)
        layout_text = TABS_LAYOUT.read_text()
        assert layout_text.count('<Tabs.Screen') == 6, f'tab count changed: {layout_text.count("<Tabs.Screen")}'
        # Menu deve contenere la voce nuova
        menu_text = MENU.read_text()
        assert '/safe-previews' in menu_text, 'menu does not link to /safe-previews'
        assert 'Sistemi in preparazione' in menu_text
        # Count menu voices added must match marker
        assert m['menu_entry_added']['voices_added_count'] == 1
    print(f'[PASS] PROJECT_Z Track B menu/hub wiring — verdict={m["verdict"]}, hub_actions=0, new_tabs=0, menu_voices_added={m["menu_entry_added"]["voices_added_count"] if m["verdict"]=="TRACK_B_SAFE_MENU_OR_PREVIEW_HUB_WIRED_SAFE" else 0}')
    return 0
if __name__ == '__main__':
    sys.exit(main())
