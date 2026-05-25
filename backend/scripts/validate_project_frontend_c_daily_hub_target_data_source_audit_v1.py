#!/usr/bin/env python3
import json, sys
from pathlib import Path
M = Path('/app/data/design/frontend/project_frontend_c_daily_hub_target_data_source_audit_v1.json')
VALID_CLASS = {'LINK_READY','READ_ONLY_STATUS_READY','DISABLED_LOCKED','EXISTING_SCREEN_LINK_ONLY','BACKEND_UNCLEAR_LINK_ONLY','DO_NOT_SHOW'}
def main():
    m = json.loads(M.read_text())
    assert m['verdict'] == 'TRACK_A_DAILY_HUB_TARGET_AND_DATA_SOURCE_AUDIT_READY'
    assert m['hub_will_call_claim_endpoint'] is False
    assert m['hub_will_call_mutating_endpoint'] is False
    assert m['hub_only_navigation'] is True
    targets = m['targets_classified']
    assert len(targets) >= 5
    for t in targets:
        assert t['class'] in VALID_CLASS, f'invalid class {t["class"]}'
    # Verify routes referenced exist for include_in_hub=true
    for t in targets:
        if t['include_in_hub'] and t.get('existing_route'):
            route = t['existing_route'].lstrip('/')
            if route:
                assert Path(f'/app/frontend/app/{route}.tsx').exists() or Path(f'/app/frontend/app/(tabs)/{route}.tsx').exists(), f'route file missing for {t["id"]}: {route}'
    print(f'[PASS] FC Track A target audit READY — targets={len(targets)}, include_in_hub={sum(1 for t in targets if t["include_in_hub"])}')
    return 0
if __name__ == '__main__': sys.exit(main())
