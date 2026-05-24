#!/usr/bin/env python3
# PROJECT_Z TRACK D — HOUSING PREVIEW MOBILE POLISH VALIDATOR
import json, sys, re
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_z_housing_preview_mobile_polish_v1.json')
ROUTE = Path('/app/frontend/app/housing-preview.tsx')

def main():
    if not MARKER.exists():
        print('[FAIL] marker missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_D_HOUSING_PREVIEW_MOBILE_POLISH_READY'
    assert ROUTE.exists()
    text = ROUTE.read_text()
    assert 'bonus e assegnazioni non ancora attivi' in text, 'banner copy not updated to track D spec'
    assert 'SafeAreaView' in text
    assert 'preview_503' in text
    # Only GET
    for pat in [r"method:\s*['\"]POST", r"method:\s*['\"]PUT", r"method:\s*['\"]DELETE", r"method:\s*['\"]PATCH"]:
        assert not re.search(pat, text), f'forbidden http method: {pat}'
    # No live bonus/spend/assignment
    for pat in [r'\bAttiva Bonus\b', r'\bSpendi\b', r'\bAssegna Residente\b', r'\bUpgrade Stanza\b']:
        assert not re.search(pat, text, flags=re.IGNORECASE), f'forbidden token: {pat}'
    assert m['polish_applied']['503_handled_gracefully'] is True
    assert m['verified_clean']['only_GET_endpoint_calls'] is True
    print('[PASS] PROJECT_Z Track D housing preview polish READY — banner_copy_v2=True, 503_graceful=True, GET_only=True')
    return 0
if __name__ == '__main__':
    sys.exit(main())
