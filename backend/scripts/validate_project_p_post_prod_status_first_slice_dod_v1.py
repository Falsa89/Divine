#!/usr/bin/env python3
"""PROJECT_P Track G validator — post-prod DoD."""
import json, sys
from pathlib import Path
M = Path('/app/data/design/status_effects/project_p_post_prod_status_first_slice_dod_v1.json')


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    m = json.loads(M.read_text())
    allowed = ('TRACK_G_POST_PROD_STATUS_FIRST_SLICE_DOD_GREEN', 'TRACK_G_POST_PROD_STATUS_FIRST_SLICE_DOD_READY_NOT_APPLIED_PENDING_APPROVAL')
    if m.get('verdict') not in allowed: fail(f'verdict not allowed: {m.get("verdict")}')
    dod = m.get('definition_of_done_for_status_first_slice', [])
    if len(dod) < 5: fail('DoD list too short')
    print(f'[PASS] PROJECT_P Track G DoD: completion={m.get("current_dod_completion", 0)} verdict={m.get("verdict")}')
    sys.exit(0)


if __name__ == '__main__': main()
