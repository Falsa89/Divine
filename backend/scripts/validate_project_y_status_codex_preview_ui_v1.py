#!/usr/bin/env python3
# PROJECT_Y TRACK E — STATUS CODEX PREVIEW UI VALIDATOR
import json, sys, re
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_y_status_codex_preview_ui_v1.json')
ROUTE = Path('/app/frontend/app/status-codex.tsx')
FORBIDDEN_TOKENS = [r'Attiva Status', r'Rollout Prod', r'Toggle Runtime', r'STATUS_RUNTIME_SECOND_SLICE_ENABLED\s*=']

def main():
    if not MARKER.exists():
        print('[FAIL] marker missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_E_STATUS_CODEX_PREVIEW_UI_READY'
    assert ROUTE.exists(), 'status-codex.tsx missing'
    text = ROUTE.read_text()
    assert 'SafeFeatureCard' in text
    assert 'FIRST_SLICE' in text and 'SECOND_SLICE' in text
    assert 'In attesa di firme PROD_ROLLOUT_*' in text
    for pat in FORBIDDEN_TOKENS:
        assert not re.search(pat, text), f'forbidden token: {pat}'
    assert m['runtime_toggle_button'] is False
    assert m['status_activation_button'] is False
    assert m['prod_rollout_button'] is False
    assert m['flag_state_unchanged'] is True
    assert m['families_first_slice_count'] == 4
    assert m['families_second_slice_count'] == 4
    print(f'[PASS] PROJECT_Y Track E status codex READY — first_slice={m["families_first_slice_count"]}, second_slice={m["families_second_slice_count"]}, no_toggles=True')
    return 0

if __name__ == '__main__':
    sys.exit(main())
