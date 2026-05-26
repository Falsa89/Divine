#!/usr/bin/env python3
# PROJECT_SOUL_FORGE_EMERGENCY_RESTORE Track B — visible screen restored.
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/soul_forge/emergency_restore_track_b_visible_screen_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_B_SOUL_FORGE_VISIBLE_SCREEN_RESTORED_SAFE'
    assert md5(F) == d['soul_forge_tsx_md5_post']
    t = F.read_text()
    # canonical fix patterns
    assert 'bodyScroll' in t, 'outer ScrollView style missing'
    assert 'useSafeAreaInsets' in t, 'safe area insets hook missing'
    # fail-safe states
    assert 'loadError' in t, 'error state missing'
    assert 'showEmptyState' in t, 'empty state guard missing'
    assert 'Promise.allSettled' in t, 'best-effort secondary fetches missing'
    # behavior preserved
    rules = d['behavior_rules_preserved']
    for k in ('4plus_protected_by_default','protected_flags_locked_favorite_native_event_unique_excluded',
              'team_heroes_excluded','override_toggle_present','typed_CONFERMA_required_for_risky_forge',
              'reward_formula_unchanged'):
        assert rules[k] is True, f'rule {k} must be True'
    assert rules['forge_mutation_endpoint_unchanged'] == '/api/soul/forge'
    assert d['backend_changes'] == 0 and d['db_writes'] == 0
    print('[PASS] EMERGENCY_RESTORE Track B visible screen restored')
    return 0
if __name__ == '__main__': sys.exit(main())
