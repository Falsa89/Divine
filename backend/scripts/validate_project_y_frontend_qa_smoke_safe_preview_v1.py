#!/usr/bin/env python3
# PROJECT_Y TRACK G — FRONTEND QA SMOKE SAFE PREVIEW VALIDATOR
import json, sys, re
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_y_frontend_qa_smoke_safe_preview_v1.json')
ROUTES = [
    Path('/app/frontend/app/artifacts-preview.tsx'),
    Path('/app/frontend/app/housing-preview.tsx'),
    Path('/app/frontend/app/status-codex.tsx'),
]
GLOBAL_FORBIDDEN = [r'\bEvoca ora\b', r'\bImporta Artefatto\b', r'\bAttiva Bonus\b', r'\bCambia Server\b', r'\bSpendi AF2N\b']
MUTATING_API_PATTERNS = [r'/api/gacha/pull', r'/api/artifacts/pull', r'/api/artifacts/fuse', r'/api/server/select', r'/api/affinity/gift-spend', r'/api/battlepass/buy-premium']

def main():
    if not MARKER.exists():
        print('[FAIL] marker missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_G_FRONTEND_QA_SMOKE_SAFE_PREVIEW_READY'
    assert m['credentials_required'] is False
    qa = m['qa_checks']
    assert qa['no_live_action_buttons'] is True
    assert qa['no_direct_mutation_endpoint_calls'] is True
    assert qa['only_GET_endpoint_calls'] is True
    # Re-verifica empirica
    for r in ROUTES:
        assert r.exists(), f'route missing: {r}'
        text = r.read_text()
        for pat in GLOBAL_FORBIDDEN:
            assert not re.search(pat, text, flags=re.IGNORECASE), f'{r.name}: forbidden label {pat}'
        for pat in MUTATING_API_PATTERNS:
            assert not re.search(pat, text), f'{r.name}: mutating API call {pat}'
    print(f'[PASS] PROJECT_Y Track G QA smoke READY — routes_checked={len(ROUTES)}, mutation_calls=0, forbidden_labels=0, only_GET={qa["only_GET_endpoint_calls"]}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
