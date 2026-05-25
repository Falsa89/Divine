#!/usr/bin/env python3
# ALIGNMENT_FIX Track C — backend/frontend wiring matrix.
import json, sys
from pathlib import Path
P = Path('/app/data/design/audit/alignment_fix/backend_frontend_wiring_matrix_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_C_BACKEND_FRONTEND_WIRING_MATRIX_REFRESH_READY'
    wm = d['wiring_matrix']
    assert len(wm) >= 25
    allowed = {'LIVE', 'LOCKED', 'LOCKED_PREVIEW', 'PREVIEW', 'DEV_HIDDEN',
               'LEGACY', 'MISSING_BACKEND', 'BACKEND_ONLY', 'PARTIAL',
               'NEEDS_FIX', 'GUARDED_DESTRUCTIVE'}
    feats = {e['feature'] for e in wm}
    must = {'gacha', 'artifacts_live', 'artifacts_preview', 'shop', 'item_shop',
            'battlepass', 'vip', 'soul_forge', 'heroes', 'menu', 'daily_hub',
            'safe_previews', 'servers'}
    missing = must - feats
    assert not missing, f'missing wiring features: {missing}'
    for e in wm:
        assert e['state'] in allowed, f'bad state for {e["feature"]}: {e["state"]}'
        for k in ('route', 'menu_visible', 'backend_endpoints', 'methods',
                  'mutation', 'mobile_qa', 'priority'):
            assert k in e
    assert d['db_writes'] == 0 and d['backend_changes'] == 0
    print(f"[PASS] ALIGN-FIX Track C wiring matrix \u2014 features={len(wm)} states={d['state_counts']}")
    return 0
if __name__ == '__main__': sys.exit(main())
