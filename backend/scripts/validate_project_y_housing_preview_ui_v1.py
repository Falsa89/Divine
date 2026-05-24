#!/usr/bin/env python3
# PROJECT_Y TRACK D — HOUSING PREVIEW UI VALIDATOR
import json, sys, re
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_y_housing_preview_ui_v1.json')
ROUTE = Path('/app/frontend/app/housing-preview.tsx')
FORBIDDEN_TOKENS = [r'\bAttiva Bonus\b', r'\bSpendi\b', r'\bAssegna Residente\b', r'\bUpgrade Stanza\b']
# Must call only GET endpoint
FORBIDDEN_HTTP = [r"method:\s*['\"]POST", r"method:\s*['\"]PUT", r"method:\s*['\"]DELETE", r"method:\s*['\"]PATCH"]

def main():
    if not MARKER.exists():
        print('[FAIL] marker missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_D_HOUSING_PREVIEW_UI_READY'
    assert ROUTE.exists(), 'housing-preview.tsx missing'
    text = ROUTE.read_text()
    assert 'SafeFeatureCard' in text
    assert '/api/housing/preview' in text
    assert 'preview_503' in text and 'state === \'preview_503\'' in text
    assert 'Dimora Divina in preparazione' in text
    for pat in FORBIDDEN_TOKENS:
        assert not re.search(pat, text, flags=re.IGNORECASE), f'forbidden token: {pat}'
    for pat in FORBIDDEN_HTTP:
        assert not re.search(pat, text), f'forbidden http method: {pat}'
    assert m['live_bonus_button'] is False
    assert m['room_upgrade_button'] is False
    assert m['resident_assignment_button'] is False
    assert m['currency_spend_button'] is False
    assert m['endpoint_503_handled'] is True
    print(f'[PASS] PROJECT_Y Track D housing preview READY — 503_handled=True, locked_cards={m["locked_feature_cards"]}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
