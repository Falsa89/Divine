#!/usr/bin/env python3
# PROJECT_BATCH_1_V2 Track G validator (mobile QA checklist coverage).
import json, sys
from pathlib import Path
J = Path('/app/data/design/audit/batch1_v2/track_g_mobile_qa_requirements_v1.json')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_G_POST_LOCK_MOBILE_QA_AND_REGRESSION_REQUIREMENTS_READY'
    assert d['db_writes'] == 0
    assert d['backend_changes'] == 0
    cl = d['mobile_qa_checklist']
    assert len(cl) >= 9
    areas = {e['area'] for e in cl}
    must = {'gacha', 'artifacts', 'shop', 'item-shop', 'battlepass', 'vip', 'soul_forge', 'menu', 'regression'}
    missing = must - areas
    assert not missing, f'mobile QA missing areas: {missing}'
    for e in cl:
        assert len(e['steps']) >= 1, f'no steps for area {e["area"]}'
    print(f"[PASS] BATCH1-V2 Track G mobile QA \u2014 areas={len(areas)}")
    return 0
if __name__ == '__main__': sys.exit(main())
