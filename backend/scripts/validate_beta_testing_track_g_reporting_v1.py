#!/usr/bin/env python3
# BETA_TESTING Track G — reporting & artifact directories standardized.
import json, sys
from pathlib import Path
J = Path('/app/data/design/testing/beta_testing_track_g_reporting_v1.json')
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_G_BETA_REPORTING_AND_SCREENSHOT_ARTIFACTS_STANDARDIZED'
    for rel in d['directories_created']:
        p = Path('/app/' + rel)
        assert p.exists() and p.is_dir(), f'directory missing: {rel}'
    # The static audit report must exist (it is the deterministic artifact).
    aud = Path('/app/' + d['standard_output_paths']['player_route_static_audit_latest'])
    assert aud.exists(), 'player_route_static_audit_latest.json missing'
    print('[PASS] BETA_TESTING Track G reporting paths standardized')
    return 0
if __name__ == '__main__': sys.exit(main())
