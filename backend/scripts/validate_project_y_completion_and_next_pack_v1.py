#!/usr/bin/env python3
# PROJECT_Y TRACK H — COMPLETION & NEXT PACK VALIDATOR
import json, sys
from pathlib import Path
MARKER = Path('/app/data/design/project_management/project_y_completion_and_next_pack_v1.json')

def main():
    if not MARKER.exists():
        print('[FAIL] marker missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_H_PROJECT_Y_COMPLETION_AND_NEXT_PACK_READY'
    assert m['project_y_closed_as'] == 'PROJECT_Y_FRONTEND_SAFE_PREVIEW_UI_IMPLEMENTATION_COMPLETE'
    assert m['recommended_next_pack_primary'] == 'PROJECT_Z_FRONTEND_SAFE_PREVIEW_POLISH_AND_MOBILE_QA_PACK'
    assert m['frontend_integration_readiness_post'] >= 45
    # Verify implemented files exist
    for path_str in [
        '/app/frontend/components/SafeFeatureCard.tsx',
        '/app/frontend/app/artifacts-preview.tsx',
        '/app/frontend/app/housing-preview.tsx',
        '/app/frontend/app/status-codex.tsx',
    ]:
        assert Path(path_str).exists(), f'implemented file missing: {path_str}'
    print(f'[PASS] PROJECT_Y Track H completion READY — implemented={len(m["implemented_in_pack_y"])}, deferred={len(m["deferred_to_followup"])}, fe_readiness={m["frontend_integration_readiness_post"]}%, next={m["recommended_next_pack_primary"]}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
