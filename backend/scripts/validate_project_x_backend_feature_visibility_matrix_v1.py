#!/usr/bin/env python3
# PROJECT_X TRACK B — BACKEND FEATURE / ENDPOINT VISIBILITY MATRIX VALIDATOR
import json, sys
from pathlib import Path
MARKER = Path('/app/data/design/frontend/project_x_backend_feature_visibility_matrix_v1.json')
VALID_CLASSES = {
    'VISIBLE_READY', 'READ_ONLY_PREVIEW_READY', 'FLAG_GATED_DISABLED_503',
    'DRY_RUN_ONLY', 'ADMIN_DEV_ONLY', 'BLOCKED_PENDING_APPROVAL',
    'DO_NOT_SHOW_PLAYER', 'LEGACY_DEPRECATED',
}
REQUIRED_FEATURES = {
    'server_profiles_preview', 'housing_preview', 'artifact_bible_dry_run',
    'status_first_slice', 'status_second_slice', 'af2n_canary',
    'gacha_summon', 'economy_battle_pass', 'hero_collection', 'combat_battle',
    'qa_mobile_smoke_dev_tools',
}

def main():
    if not MARKER.exists():
        print('[FAIL] marker JSON missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['verdict'] == 'TRACK_B_BACKEND_FEATURE_ENDPOINT_VISIBILITY_MATRIX_READY'
    assert m['audit_only'] is True
    assert m['backend_mutation'] is False
    assert set(m['visibility_classes']) == VALID_CLASSES
    feats = set(m['features'].keys())
    missing = REQUIRED_FEATURES - feats
    assert not missing, f'required features missing: {missing}'
    for k, v in m['features'].items():
        assert v['class'] in VALID_CLASSES, f'invalid class for {k}: {v["class"]}'
    # Specific invariants
    assert m['features']['server_profiles_preview']['current_status_code'] == 503
    assert m['features']['housing_preview']['current_status_code'] == 503
    assert m['features']['status_second_slice']['class'] == 'BLOCKED_PENDING_APPROVAL'
    print(f'[PASS] PROJECT_X Track B endpoint visibility matrix READY — features_classified={len(m["features"])}, classes_used={len({v["class"] for v in m["features"].values()})}, total_endpoints_audited={m["total_backend_endpoints_audited"]}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
