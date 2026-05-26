#!/usr/bin/env python3
# BETA_TESTING Track D — locked surfaces static tests.
import json, sys, re
from pathlib import Path
J = Path('/app/data/design/testing/beta_testing_track_d_locked_surfaces_v1.json')
def strip_comments(t):
    t = re.sub(r'/\*[\s\S]*?\*/', '', t)
    t = re.sub(r'(^|[^:\"\'])//[^\n]*', r'\1', t)
    return t
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_D_LOCKED_SURFACES_STATIC_TESTS_READY'
    for surf in d['locked_surfaces']:
        p = Path('/app/' + surf['file'])
        assert p.exists(), f'locked file missing: {surf["file"]}'
        code = strip_comments(p.read_text())
        assert surf['flag_marker'].split(' = ')[0] in code or surf['flag_marker'] in code, \
            f'lock marker {surf["flag_marker"]!r} missing in {surf["file"]}'
        # Forbidden live-action labels must not be visible
        for label in d['forbidden_live_action_labels']:
            assert label not in code, f'forbidden live action label {label!r} visible in {surf["file"]}'
    print('[PASS] BETA_TESTING Track D locked surfaces static')
    return 0
if __name__ == '__main__': sys.exit(main())
