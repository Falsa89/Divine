#!/usr/bin/env python3
# PROJECT_Y TRACK C — ARTIFACT COLLECTION PREVIEW UI VALIDATOR
import json, sys, re
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_y_artifact_collection_preview_ui_v1.json')
ROUTE = Path('/app/frontend/app/artifacts-preview.tsx')
FORBIDDEN = [r'\bSummon\b', r'\bEvoca ora\b', r'\bImporta Artefatto\b', r'\bUpgrade\b', r'\bAttiva Bonus\b']
FORBIDDEN_API = [r'/api/artifacts/pull', r'/api/artifacts/fuse', r'/api/artifacts/import']

def main():
    if not MARKER.exists():
        print('[FAIL] marker missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_C_ARTIFACT_COLLECTION_PREVIEW_UI_READY'
    assert ROUTE.exists(), 'artifacts-preview.tsx missing on disk'
    text = ROUTE.read_text()
    assert 'SafeFeatureCard' in text
    # accetta sia la copy v1 (Pack Y) che la copy v2 (aggiornata in Pack Z Track C)
    assert ('evocazione e bonus non ancora attivi' in text) or ('evocazione, import e bonus non ancora attivi' in text)
    for pat in FORBIDDEN:
        assert not re.search(pat, text, flags=re.IGNORECASE), f'forbidden token present: {pat}'
    for pat in FORBIDDEN_API:
        assert not re.search(pat, text), f'forbidden API call present: {pat}'
    assert m['summon_button'] is False
    assert m['import_button'] is False
    assert m['upgrade_button'] is False
    assert m['bonus_activation_button'] is False
    assert m['interactive_backend_calls'] is False
    print(f'[PASS] PROJECT_Y Track C artifact preview READY — locked_cards={m["locked_cards_count"]}, no_live_actions=True')
    return 0

if __name__ == '__main__':
    sys.exit(main())
