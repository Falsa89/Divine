#!/usr/bin/env python3
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_roadmap_and_approval_gates_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_G_SERVER_PROFILES_ROADMAP_AND_APPROVAL_GATES_READY'
    assert d['audit_mode'] == 'roadmap_only'
    assert d['db_writes'] == 0 and d['backend_changes'] == 0
    assert d['global_markers']['TRACK_G_SERVER_PROFILES_ROADMAP_APPROVAL_GATES_APPROVAL'] == 'true'
    stages = d['stages']
    assert isinstance(stages, list) and len(stages) >= 9
    nums = [s['n'] for s in stages]
    assert nums == sorted(nums)
    for s in stages:
        assert s.get('approval_marker'), f'stage {s.get("n")} missing approval_marker'
        assert s.get('status') == 'PENDING'
    # Required keywords
    names = ' '.join(s['name'] for s in stages)
    for kw in ['AUTH', 'SEED', 'PRE_HOME', 'DUAL_READ', 'UI_CUTOVER', 'DUAL_WRITE', 'LEGACY']:
        assert kw in names, f'missing roadmap stage keyword {kw}'
    print(f"[PASS] AUTH-HARDEN Track G roadmap READY \u2014 stages={len(stages)}")
    return 0
if __name__ == '__main__': sys.exit(main())
