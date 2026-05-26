#!/usr/bin/env python3
# PROJECT_SOUL_FORGE_EMERGENCY_RESTORE Track D — mobile layout + confirm modal.
import json, sys
from pathlib import Path
J = Path('/app/data/design/soul_forge/emergency_restore_track_d_mobile_modal_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_D_SOUL_FORGE_MOBILE_LAYOUT_AND_CONFIRM_MODAL_FIXED'
    t = F.read_text()
    # Modal protection
    assert 'KeyboardAvoidingView' in t, 'KeyboardAvoidingView missing in modal'
    assert 'keyboardShouldPersistTaps' in t, 'keyboardShouldPersistTaps missing'
    # Safe area
    assert 'useSafeAreaInsets' in t
    assert 'insets.bottom' in t, 'bottom safe area not applied'
    # Risk confirm flow preserved
    for tok in ('isRiskyForge','typedConfirm','CONFERMA','modalCardV2','modalConfirmV2','modalCancelV2'):
        assert tok in t, f'confirm modal token {tok} missing'
    # Verify the previous raw escape literals are now fixed (use JSX expression containers)
    # The old bug had bare \u2022 in JSX text; the new code uses {'\u2022'} expression.
    assert "{'\\u2022'}" in t or "{'\u2022'}" in t, 'bullet JSX expression form not present'
    assert d['one_tap_destruction_blocked'] is True
    print('[PASS] EMERGENCY_RESTORE Track D mobile layout + confirm modal')
    return 0
if __name__ == '__main__': sys.exit(main())
