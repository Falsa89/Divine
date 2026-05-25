#!/usr/bin/env python3
import json, sys
from pathlib import Path
M = Path('/app/data/design/frontend/project_frontend_b_heroes_flow_audit_v1.json')
def main():
    m = json.loads(M.read_text())
    assert m['verdict'] == 'TRACK_A_HEROES_COLLECTION_AND_HERO_DETAIL_FLOW_AUDIT_READY'
    assert m['audit_only'] is True
    assert m['frontend_mutation'] is False
    assert len(m['routes_audited']) >= 6
    assert len(m['flow_steps']) >= 6
    # verify actual files exist
    for f in ['/app/frontend/app/(tabs)/heroes.tsx', '/app/frontend/app/hero-collection.tsx', '/app/frontend/app/hero-detail.tsx']:
        assert Path(f).exists(), f'missing: {f}'
    print(f'[PASS] FB Track A heroes flow audit READY — routes={len(m["routes_audited"])}, flow_steps={len(m["flow_steps"])}, gaps={len(m["gaps_identified"])}')
    return 0
if __name__ == '__main__': sys.exit(main())
