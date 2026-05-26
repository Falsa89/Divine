#!/usr/bin/env python3
# PROJECT_SOUL_FORGE_EMERGENCY_RESTORE Track A — root cause documented.
import json, sys
from pathlib import Path
J = Path('/app/data/design/soul_forge/emergency_restore_root_cause_v1.json')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_A_SOUL_FORGE_BLANK_SCREEN_ROOT_CAUSE_IDENTIFIED'
    assert 'RC1_BROKEN_FLEX_DISTRIBUTION_IN_BODY_COLUMN_STACK' in d['root_cause_primary']['id']
    assert d['root_cause_secondary']['line'] == 458
    assert 'no_validator_weakening' in d['forbidden_kept_clean']
    assert d['files_to_change_in_this_pack'] == ['frontend/app/soul-forge.tsx']
    print('[PASS] EMERGENCY_RESTORE Track A root cause documented')
    return 0
if __name__ == '__main__': sys.exit(main())
