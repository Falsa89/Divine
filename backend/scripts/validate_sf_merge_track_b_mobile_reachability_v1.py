#!/usr/bin/env python3
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
    assert 'forgeScrollContent' in t, 'ScrollView wrapper missing'
    assert "flexDirection: 'column'" in t, 'body should be column on mobile'
    rules = d['behavior_rules_preserved']
    for k in ('4plus_protection','team_locked_favorite_native_event_unique_blocked',
              'select_all_skips_high_rarity','typed_CONFERMA_for_risky'):
        assert rules[k] is True
    assert d['backend_changes'] == 0 and d['db_writes'] == 0
    print('[PASS] SF-MERGE Track B mobile reachability')
    return 0
if __name__=='__main__': sys.exit(main())
