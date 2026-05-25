#!/usr/bin/env python3
import json, sys
from pathlib import Path
M = Path('/app/data/design/frontend/project_frontend_b_qa_backlog_v1.json')
VALID_P = {'P1', 'P2', 'P3'}
def main():
    m = json.loads(M.read_text())
    assert m['verdict'] == 'TRACK_G_CORE_USER_FLOW_QA_BACKLOG_AND_PRIORITIZATION_READY'
    backlog = m['qa_backlog']
    assert len(backlog) >= 10
    for it in backlog:
        assert it['priority'] in VALID_P
        assert 'id' in it and 'area' in it and 'description' in it
    s = m['priority_summary']
    assert s['P1'] + s['P2'] + s['P3'] == len(backlog)
    print(f'[PASS] FB Track G QA backlog READY — items={len(backlog)}, P1={s["P1"]}, P2={s["P2"]}, P3={s["P3"]}')
    return 0
if __name__ == '__main__': sys.exit(main())
