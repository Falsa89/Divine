#!/usr/bin/env python3
import json, sys
from pathlib import Path
M = Path('/app/data/design/frontend/project_frontend_b_economy_flow_audit_v1.json')
def main():
    m = json.loads(M.read_text())
    assert m['verdict'] == 'TRACK_D_ECONOMY_SHOP_BATTLE_PASS_DAILY_FLOW_AUDIT_READY'
    assert m['audit_only'] is True
    assert any('economy/pricing logic' in s for s in m['do_not_touch'])
    for f in ['/app/frontend/app/economy.tsx', '/app/frontend/app/shop.tsx', '/app/frontend/app/battlepass.tsx']:
        assert Path(f).exists()
    print(f'[PASS] FB Track D economy flow audit READY — routes={len(m["routes_audited"])}, gaps={len(m["gaps_identified"])}')
    return 0
if __name__ == '__main__': sys.exit(main())
