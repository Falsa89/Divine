#!/usr/bin/env python3
# ALIGNMENT_FIX Track B — Soul Forge high-rarity override fix.
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/audit/alignment_fix/track_b_soul_forge_fix_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_B_SOUL_FORGE_HIGH_RARITY_OVERRIDE_FIXED_SAFE'
    assert d['soul_forge_mode_preserved'] is True
    assert d['backend_changes'] == 0 and d['db_writes'] == 0
    assert d['reward_formula_changes'] == 0
    assert d['hero_deletion'] == 0 and d['user_heroes_mutation'] == 0
    rules = d['behavior_rules_preserved']
    for k in ('high_rarity_protected_by_default', '4_plus_selectable_only_with_override',
              'team_locked_favorite_native_event_unique_always_blocked',
              'select_all_skips_high_rarity', 'typed_CONFERMA_for_risky',
              'exact_breakdown_in_modal'):
        assert rules[k] is True, f'rule {k} must be True'
    assert md5(F) == d['soul_forge_tsx_md5_post'], f'drift: {md5(F)}'
    text = F.read_text()
    # discoverability checks
    assert "Eroe protetto" in text or 'Sblocca ora' in text, 'alert feedback missing'
    assert 'overrideStatusBannerV2' in text, 'prominent status banner missing'
    assert 'ATTIVO' in text, 'active label missing'
    # rule preservation checks (V2 invariants)
    for tok in ['HIGH_RARITY_PROTECT_MIN', 'PROTECTED_FLAGS', 'requestForge',
                'confirmForge', 'CONFERMA', 'typedConfirm']:
        assert tok in text, f'missing invariant token: {tok}'
    assert '/api/soul/forge' in text
    print('[PASS] ALIGN-FIX Track B soul forge override fix')
    return 0
if __name__ == '__main__': sys.exit(main())
