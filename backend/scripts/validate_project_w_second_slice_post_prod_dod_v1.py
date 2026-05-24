#!/usr/bin/env python3
# PROJECT_W TRACK G — POST-PROD DOD VALIDATOR
import json, sys
from pathlib import Path
MARKER = Path('/app/data/design/project_management/project_w_second_slice_post_prod_dod_v1.json')

def main():
    if not MARKER.exists():
        print('[FAIL] marker JSON missing'); return 1
    m = json.loads(MARKER.read_text())
    valid = (
        'TRACK_G_SECOND_SLICE_POST_PROD_DOD_COMPLETE',
        'TRACK_G_SECOND_SLICE_POST_PROD_DOD_PENDING_APPROVAL',
    )
    assert m['verdict'] in valid
    if m['verdict'] == 'TRACK_G_SECOND_SLICE_POST_PROD_DOD_COMPLETE':
        c = m['dod_components']
        assert c['prod_signatures_complete'] is True
        assert c['stage_markers_complete'] is True
        assert c['all_stages_green'] is True
        assert c['rollback_drill_documented'] is True
    print(f'[PASS] PROJECT_W Track G post-prod DoD — verdict={m["verdict"]}, applied={m["second_slice_prod_applied"]}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
