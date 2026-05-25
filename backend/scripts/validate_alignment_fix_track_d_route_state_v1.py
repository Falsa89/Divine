#!/usr/bin/env python3
# ALIGNMENT_FIX Track D — player-visible route state enforcement.
import json, sys
from pathlib import Path
P = Path('/app/data/design/audit/alignment_fix/player_visible_route_state_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_D_PLAYER_VISIBLE_ROUTE_STATE_ENFORCEMENT_READY'
    allowed = set(d['approved_states'])
    assert allowed == {'SAFE_LIVE','LOCKED_PREVIEW','READ_ONLY','GUARDED_DESTRUCTIVE',
                       'DEV_HIDDEN','NEEDS_BACKEND','NEEDS_DESIGN'}
    routes = d['player_visible_routes']
    assert len(routes) >= 18
    for r in routes:
        assert r['state'] in allowed, f'illegal state on {r["route"]}: {r["state"]}'
    must_routes = {'/gacha','/artifacts','/artifacts-preview','/shop','/item-shop',
                   '/battlepass','/vip','/soul-forge','/(tabs)/heroes','/(tabs)/menu',
                   '/daily-hub','/safe-previews','/servers'}
    have = {r['route'] for r in routes}
    missing = must_routes - have
    assert not missing, f'missing player-visible routes: {missing}'
    # eventuali blocker documentati
    blockers = d.get('blockers_not_safely_fixable_in_this_pack', [])
    for b in blockers:
        assert 'next_pack' in b
    assert d['db_writes'] == 0 and d['backend_changes'] == 0
    print(f"[PASS] ALIGN-FIX Track D route state \u2014 routes={len(routes)} blockers={len(blockers)}")
    return 0
if __name__ == '__main__': sys.exit(main())
