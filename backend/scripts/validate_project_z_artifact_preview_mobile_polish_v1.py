#!/usr/bin/env python3
# PROJECT_Z TRACK C — ARTIFACT PREVIEW MOBILE POLISH VALIDATOR
import json, sys, re
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_z_artifact_preview_mobile_polish_v1.json')
ROUTE = Path('/app/frontend/app/artifacts-preview.tsx')

def main():
    if not MARKER.exists():
        print('[FAIL] marker missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_C_ARTIFACT_PREVIEW_MOBILE_POLISH_READY'
    assert ROUTE.exists()
    text = ROUTE.read_text()
    # banner copy aggiornato secondo spec
    expected = 'Artefatti in anteprima \u2014 evocazione, import e bonus non ancora attivi.'
    # Compare allowing both unicode & em-dash literal
    assert 'evocazione, import e bonus non ancora attivi' in text, 'banner copy not updated to track C spec'
    assert 'SafeAreaView' in text
    assert 'ScrollView' in text
    # No summon/import/upgrade/bonus action
    for pat in [r'\bSummon\b', r'\bImporta Artefatto\b', r'\bUpgrade\b', r'\bAttiva Bonus\b']:
        assert not re.search(pat, text, flags=re.IGNORECASE), f'forbidden: {pat}'
    assert m['polish_applied']['safe_area_view_used'] is True
    assert m['verified_clean']['no_horizontal_overflow_at_390x844'] is True
    print('[PASS] PROJECT_Z Track C artifact preview polish READY — banner_copy_v2=True, safe_area=True, no_live_actions=True')
    return 0
if __name__ == '__main__':
    sys.exit(main())
