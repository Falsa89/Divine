#!/usr/bin/env python3
# BETA_TESTING Track C — Soul Forge static regression (no modal path).
import json, sys, hashlib, re
from pathlib import Path
J = Path('/app/data/design/testing/beta_testing_track_c_soul_forge_regression_v1.json')
F = Path('/app/frontend/app/soul-forge.tsx')
def md5(p): return hashlib.md5(p.read_bytes()).hexdigest()
def strip_comments(t):
    t = re.sub(r'/\*[\s\S]*?\*/', '', t)
    t = re.sub(r'(^|[^:\"\'])//[^\n]*', r'\1', t)
    return t
def main():
    d = json.loads(J.read_text())
    assert d['verdict'] == 'TRACK_C_SOUL_FORGE_REGRESSION_STATIC_TESTS_READY'
    assert md5(F) == d['file_md5_pinned']
    raw = F.read_text()
    code = strip_comments(raw)
    # required markers in CODE (post comment strip)
    for m in d['required_markers']:
        assert m in code, f'required marker missing in code: {m!r}'
    # forbidden modal-path markers must not appear in code (comments OK)
    for m in d['forbidden_modal_path_markers']:
        assert m not in code, f'forbidden modal-path marker present in CODE: {m!r}'
    # defensive render markers
    for m in d['defensive_render_markers']:
        assert m in code, f'defensive render marker missing: {m!r}'
    print('[PASS] BETA_TESTING Track C soul forge regression static')
    return 0
if __name__ == '__main__': sys.exit(main())
