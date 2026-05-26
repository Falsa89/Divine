#!/usr/bin/env python3
# PROJECT_BATCH_1_V2 Track D validator (soul forge guard).
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/audit/batch1_v2/track_d_soul_forge_guard_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_D_SOUL_FORGE_PERMANENT_DESTRUCTION_GUARD_IMPLEMENTED_SAFE'
    assert d['soul_forge_mode_preserved'] is True, 'Soul Forge mode must be preserved'
    assert d['hero_deletion'] == 0
    assert d['user_heroes_mutation'] == 0
    assert d['backend_changes'] == 0
    assert d['db_writes'] == 0
    assert d['protect_min_stars'] == 4
    assert d['risky_bulk_threshold'] >= 5
    needed_layers = {
        'team_filter',
        'flag_filter_locked_favorite_native_event_unique',
        'high_rarity_default_protect_min_4\u2605',
        'multi_step_inline_confirm_panel',
        'typed_confirmation_CONFERMA_for_risky_forge',
        'exact_loss_and_gain_preview_in_modal',
    }
    have = set(d['guard_layers'])
    missing = needed_layers - have
    assert not missing, f'missing guard layers: {missing}'
    # File content checks
    text = F.read_text()
    # INLINE_CONFIRM supersession: confirmOpen was replaced by inlineConfirmOpen
    # (the multi-step confirm is now an inline panel inside the outer ScrollView,
    # not a React Native Modal, to avoid the mobile RN Modal+KAV crash). The safety
    # invariants are preserved by the inline panel.
    for tok in ['HIGH_RARITY_PROTECT_MIN', 'PROTECTED_FLAGS', 'isHeroProtectedByFlags',
                'inlineConfirmOpen', 'typedConfirm', 'overrideHighRarity', 'requestForge',
                'confirmForge', 'CONFERMA']:
        assert tok in text, f'missing token in soul-forge.tsx: {tok}'
    # /api/soul/forge call must still be present (mode preserved)
    assert '/api/soul/forge' in text
    assert md5(F) == d['soul_forge_tsx_md5_post']
    print('[PASS] BATCH1-V2 Track D soul forge guard')
    return 0
if __name__ == '__main__': sys.exit(main())
