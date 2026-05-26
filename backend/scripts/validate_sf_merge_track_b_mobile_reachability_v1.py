#!/usr/bin/env python3
# SF_MERGE Track B validator (mobile reachability).
# REALIGNED by PROJECT_SOUL_FORGE_EMERGENCY_RESTORE_AND_FULL_MERGE_FIX_PACK to the
# canonical single-outer-ScrollView layout. The previous pattern checks (inner
# forgeScrollContent ScrollView, body flexDirection:column) DESCRIBED THE BUG
# that caused the blank screen regression. The fixed pattern uses an outer
# ScrollView (bodyScroll) wrapping all content for mobile-first scroll.
import json, sys, hashlib
from pathlib import Path
J = Path('/app/data/design/audit/sf_merge/track_b_mobile_reachability_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_B_SOUL_FORGE_MOBILE_LAYOUT_REACHABILITY_FIXED_SAFE'
    assert md5(F) == d['soul_forge_tsx_md5_post']
    t = F.read_text()
    # New canonical pattern (post EMERGENCY_RESTORE)
    assert 'bodyScroll' in t, 'outer ScrollView style bodyScroll missing'
    assert 'KeyboardAvoidingView' in t, 'modal must use KeyboardAvoidingView'
    assert 'useSafeAreaInsets' in t, 'safe area insets missing'
    rules = d['behavior_rules_preserved']
    for k in ('4plus_protection','team_locked_favorite_native_event_unique_blocked',
              'select_all_skips_high_rarity','typed_CONFERMA_for_risky'):
        assert rules[k] is True
    assert d['backend_changes'] == 0 and d['db_writes'] == 0
    print('[PASS] SF-MERGE Track B mobile reachability (realigned by EMERGENCY_RESTORE)')
    return 0
if __name__=='__main__': sys.exit(main())
