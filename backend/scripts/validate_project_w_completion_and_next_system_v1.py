#!/usr/bin/env python3
# PROJECT_W TRACK H — COMPLETION & NEXT SYSTEM VALIDATOR
import json, sys
from pathlib import Path
MARKER = Path('/app/data/design/project_management/project_w_completion_and_next_system_v1.json')

def main():
    if not MARKER.exists():
        print('[FAIL] marker JSON missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_H_PROJECT_W_COMPLETION_AND_NEXT_SYSTEM_READY'
    closed_valid = (
        'PROJECT_W_STATUS_SECOND_SLICE_PROD_ROLLOUT_READY_NOT_APPLIED_PENDING_APPROVAL',
        'PROJECT_W_STATUS_SECOND_SLICE_PROD_ROLLOUT_COMPLETE',
    )
    assert m['project_w_closed_as'] in closed_valid
    assert isinstance(m['recommended_next_systems'], list) and len(m['recommended_next_systems']) >= 1
    assert m['recommended_next_primary'] in m['recommended_next_systems']
    print(f'[PASS] PROJECT_W Track H completion — closed_as={m["project_w_closed_as"]}, next_primary={m["recommended_next_primary"]}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
