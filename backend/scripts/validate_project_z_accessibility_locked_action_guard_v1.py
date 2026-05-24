#!/usr/bin/env python3
# PROJECT_Z TRACK F — ACCESSIBILITY & LOCKED ACTION GUARD VALIDATOR
import json, sys, re
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_z_accessibility_locked_action_guard_v1.json')
COMPONENT = Path('/app/frontend/components/SafeFeatureCard.tsx')
ROUTES = [
    Path('/app/frontend/app/safe-previews.tsx'),
    Path('/app/frontend/app/artifacts-preview.tsx'),
    Path('/app/frontend/app/housing-preview.tsx'),
    Path('/app/frontend/app/status-codex.tsx'),
]
FORBIDDEN_ENABLED_LABELS = [r'\bEvoca ora\b', r'\bImporta ora\b', r'\bAttiva bonus\b', r'\bCambia server\b', r'\bLancia rollout\b']

def main():
    if not MARKER.exists():
        print('[FAIL] marker missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_F_ACCESSIBILITY_AND_LOCKED_ACTION_GUARD_READY'
    assert COMPONENT.exists()
    comp = COMPONENT.read_text()
    assert 'accessibilityLabel' in comp
    assert 'accessibilityState' in comp
    assert 'isLocked ? View : TouchableOpacity' in comp
    # All routes have at least 1 accessibilityLabel on back btn
    for r in ROUTES:
        assert r.exists(), f'route missing: {r}'
        t = r.read_text()
        assert 'accessibilityLabel' in t, f'no accessibilityLabel in {r.name}'
        for pat in FORBIDDEN_ENABLED_LABELS:
            assert not re.search(pat, t, flags=re.IGNORECASE), f'{r.name}: forbidden enabled label {pat}'
    # hub uses accessibilityRole link/button
    hub_text = ROUTES[0].read_text()
    assert 'accessibilityRole' in hub_text
    assert 'accessibilityHint' in hub_text
    print(f'[PASS] PROJECT_Z Track F accessibility guard READY — routes_checked={len(ROUTES)}, forbidden_labels=0, locked_renders_View=True')
    return 0
if __name__ == '__main__':
    sys.exit(main())
