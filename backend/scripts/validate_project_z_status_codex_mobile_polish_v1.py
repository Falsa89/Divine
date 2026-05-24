#!/usr/bin/env python3
# PROJECT_Z TRACK E — STATUS CODEX MOBILE POLISH VALIDATOR
import json, sys, re
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_z_status_codex_mobile_polish_v1.json')
ROUTE = Path('/app/frontend/app/status-codex.tsx')

def main():
    if not MARKER.exists():
        print('[FAIL] marker missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_E_STATUS_CODEX_MOBILE_POLISH_READY'
    assert ROUTE.exists()
    text = ROUTE.read_text()
    assert 'FIRST_SLICE' in text and 'SECOND_SLICE' in text
    assert 'SafeAreaView' in text
    assert 'In attesa di firme PROD_ROLLOUT_*' in text
    for pat in [r'\bAttiva Status\b', r'\bRollout Prod\b', r'\bToggle Runtime\b', r'STATUS_RUNTIME_SECOND_SLICE_ENABLED\s*=']:
        assert not re.search(pat, text), f'forbidden token: {pat}'
    assert m['safety_verified']['no_runtime_toggle'] is True
    assert m['safety_verified']['no_prod_rollout_button'] is True
    print('[PASS] PROJECT_Z Track E status codex polish READY — no_runtime_toggles=True, no_rollout_buttons=True, legend_present=True')
    return 0
if __name__ == '__main__':
    sys.exit(main())
