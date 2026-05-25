#!/usr/bin/env python3
# PROJECT_MODE_WIRING_REGISTRY / TRACK F
import json, sys
from pathlib import Path

P = Path('/app/data/design/frontend/mode_smoke_test_requirements_v1.json')
REQUIRED = ['mode_id','api_smoke','frontend_smoke','mobile_smoke','no_live_action_guard','locked_state_guard','regression_validator','priority']

def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_F_MODE_SMOKE_TEST_REQUIREMENTS_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['global_markers']['TRACK_F_MODE_SMOKE_TEST_REQUIREMENTS_APPROVAL'] == 'true'
    rows = d['smoke_requirements_per_mode']
    assert isinstance(rows, list) and len(rows) >= 20
    for r in rows:
        for f in REQUIRED:
            assert f in r, f"mode {r.get('mode_id')} missing {f}"
        assert r['priority'] in ('P1','P2','P3','P4')
    # forbidden destructive smoke documented
    forb = d['forbidden_smoke_actions']
    assert any('no DB writes' in x or 'no DB' in x for x in forb)
    assert any('no fake mobile screenshots' in x for x in forb)
    s = d['summary']
    print(f"[PASS] Track F mode smoke requirements READY \u2014 modes={s['total_modes_with_smoke']}, P1={s['P1_priority']}")
    return 0
if __name__ == '__main__': sys.exit(main())
