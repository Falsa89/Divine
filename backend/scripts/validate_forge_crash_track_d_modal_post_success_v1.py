#!/usr/bin/env python3
# FORGE_CRASH Track D — modal + post-success state safe.
import json, sys
from pathlib import Path
J = Path('/app/data/design/soul_forge/forge_crash_track_d_modal_post_success_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_D_MOBILE_CONFIRM_MODAL_AND_POST_SUCCESS_STATE_SAFE'
    t = F.read_text()
    # double-submit guard in confirmForge
    assert 'if (forging) return;' in t
    # confirm button respects forging
    assert 'forging && { opacity: 0.5 }' in t, 'modal confirm dim while forging missing'
    assert "IN CORSO" in t, 'modal confirm label swap missing'
    # INLINE_CONFIRM supersession: confirmForge ora chiude il pannello inline (non un Modal),
    # ma il guardrail double-submit + label-swap-during-forging \u00e8 stato preservato sul
    # bottone finale dell'inline panel.
    # inline confirm button respects forging (uses same forging-disable + label-swap pattern)
    assert 'inlineConfirmConfirm' in t, 'inline confirm button style missing'
    # The disabled prop on the inline confirm uses the same multi-line ternary
    assert 'disabled={\n                      forging ||' in t, 'inline confirm disabled while forging missing'
    # KeyboardAvoidingView is REMOVED by INLINE_CONFIRM pack (Modal+KAV caused mobile crash).
    # The inline panel does NOT need KAV because it lives inside the outer ScrollView.
    head = t.split("from 'react-native';")[0]
    assert 'KeyboardAvoidingView' not in head, 'KAV still imported (must be removed by INLINE_CONFIRM)'
    assert d['selected_heroes_preserved_on_failure'] is True
    assert d['never_crash_app'] is True
    assert d['backend_changes'] == 0
    print('[PASS] FORGE_CRASH Track D modal + post-success safe')
    return 0
if __name__ == '__main__': sys.exit(main())
