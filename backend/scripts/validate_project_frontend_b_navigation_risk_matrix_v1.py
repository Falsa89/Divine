#!/usr/bin/env python3
import json, sys
from pathlib import Path
M = Path('/app/data/design/frontend/project_frontend_b_navigation_risk_matrix_v1.json')
VALID_RISKS = {'low', 'medium', 'high', 'high_for_polish'}
def main():
    m = json.loads(M.read_text())
    assert m['verdict'] == 'TRACK_F_FRONTEND_NAVIGATION_RISK_AND_MISSING_LINKS_MATRIX_READY'
    assert m['broad_refactor_required'] is False
    for a in m['navigation_risk_matrix']:
        assert a['risk'] in VALID_RISKS, f'invalid risk: {a["risk"]}'
    print(f'[PASS] FB Track F navigation risk matrix READY — areas={len(m["navigation_risk_matrix"])}, missing_links={len(m["missing_links"])}')
    return 0
if __name__ == '__main__': sys.exit(main())
