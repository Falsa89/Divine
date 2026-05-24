#!/usr/bin/env python3
# PROJECT_X TRACK D — FEATURE ACCESS POLICY & LOCK COPY VALIDATOR
import json, sys
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_x_feature_access_policy_lock_copy_v1.json')
REQUIRED_CLASSES = {'visible_locked', 'hidden_until_approved', 'dev_only', 'read_only_preview', 'live_feature'}

def main():
    if not MARKER.exists():
        print('[FAIL] marker JSON missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_D_FEATURE_ACCESS_POLICY_AND_LOCK_COPY_READY'
    assert m['audit_only'] is True
    assert m['player_facing_implementation'] is False
    assert set(m['access_policy_classes'].keys()) >= REQUIRED_CLASSES
    p = m['button_policy']
    assert p['no_fake_functionality'] is True
    assert p['no_claim_button_unless_endpoint_live_and_approved'] is True
    assert p['no_summon_button_unless_endpoint_live_and_approved'] is True
    assert p['no_upgrade_button_unless_endpoint_live_and_approved'] is True
    catalog = m['lock_copy_catalog_italian']
    assert all(isinstance(v, str) and len(v) > 0 for v in catalog.values())
    print(f'[PASS] PROJECT_X Track D feature access policy READY — classes={len(m["access_policy_classes"])}, lock_copy_entries={len(catalog)}, button_policy_strict=True')
    return 0

if __name__ == '__main__':
    sys.exit(main())
