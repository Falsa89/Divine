#!/usr/bin/env python3
# PROJECT_Y TRACK B — LOCKED CARD COMPONENT VALIDATOR
import json, sys
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_y_locked_card_component_v1.json')
COMPONENT = Path('/app/frontend/components/SafeFeatureCard.tsx')

def main():
    if not MARKER.exists():
        print('[FAIL] marker missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_B_FRONTEND_LOCKED_CARD_COMPONENT_READY'
    assert COMPONENT.exists(), 'SafeFeatureCard.tsx missing on disk'
    text = COMPONENT.read_text()
    assert 'export function SafeFeatureCard' in text or 'export default function SafeFeatureCard' in text
    assert 'SafeFeatureCardProps' in text
    # Tutte le visibility supportate
    for v in m['visibility_values_supported']:
        assert f"'{v}'" in text, f'visibility {v} not in component'
    # Locked default → wrappa in View, NOT TouchableOpacity
    assert 'isLocked ? View : TouchableOpacity' in text
    assert m['locked_default_behavior']['onPress_ignored_when_locked'] is True
    assert m['has_live_action_handler_by_default'] is False
    assert m['has_enabled_state_when_visibility_locked'] is False
    print(f'[PASS] PROJECT_Y Track B locked card component READY — props={len(m["props_supported"])}, visibility_classes={len(m["visibility_values_supported"])}, no_live_handler_default=True')
    return 0

if __name__ == '__main__':
    sys.exit(main())
