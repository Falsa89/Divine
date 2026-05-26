#!/usr/bin/env python3
# INLINE_CONFIRM Track C — inline confirmation panel present and correct.
import json, sys
from pathlib import Path
J = Path('/app/data/design/soul_forge/inline_confirm_track_c_panel_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_C_INLINE_CONFIRMATION_PANEL_READY_SAFE'
    t = F.read_text()
    # State and trigger
    assert 'inlineConfirmOpen' in t, 'inlineConfirmOpen state missing'
    assert 'setInlineConfirmOpen(true)' in t, 'requestForge does not open inline panel'
    assert 'setInlineConfirmOpen(false)' in t, 'confirmForge/cancel does not close inline panel'
    # Panel contents tokens
    for tok in ('inlineConfirmCard', 'inlineConfirmTitle', 'inlineConfirmBreakdown',
                'inlineConfirmActions', 'inlineConfirmCancel', 'inlineConfirmConfirm'):
        assert tok in t, f'inline panel style {tok} missing'
    # Final confirm button label
    assert 'CONFERMA FORGE' in t, 'final inline confirm button label missing'
    # Cancel label
    assert 'ANNULLA' in t, 'cancel label missing'
    # Safety: typed CONFERMA still required when risky (TextInput in inline panel)
    assert 'inlineConfirmInput' in t, 'typed CONFERMA input missing in inline'
    # Confirm calls existing confirmForge
    assert 'onPress={confirmForge}' in t, 'inline confirm must call confirmForge'
    # Safety rules preserved
    for k in ('no_one_tap_destruction','high_rarity_4plus_protection',
              'typed_CONFERMA_required_for_risky','team_heroes_excluded',
              'double_submit_guard'):
        assert d['safety_rules_preserved'][k] is True, f'safety rule {k} not preserved'
    print('[PASS] INLINE_CONFIRM Track C inline panel ready')
    return 0
if __name__ == '__main__': sys.exit(main())
