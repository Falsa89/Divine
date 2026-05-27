#!/usr/bin/env python3
"""
PROJECT_ARTIFACT_LIVE_SIGNOFF_SUITE_RUNNER_SYNC_FIX validator.

Verifies the targeted micro-fix on backend/scripts/run_hero_skill_kit_validator_suite.py:
  - top sentinel v3 still present
  - top sentinel v4 added (resync tag)
  - STAGE_7_LIVE_ACTIVATION_SIGNOFF_REGISTRATION_SENTINEL still present
  - STAGE_7_LIVE_ACTIVATION_SIGNOFF_REGISTRATION_RESYNC_v4 inline sentinel added
  - registration tuple present EXACTLY ONCE (not duplicated)
  - file is Python parseable
  - MD5 invariants unchanged (battle_engine, .env, routes/artifacts.py, frontend)
  - .env has NOT been modified (no live markers injected)
"""
import ast
import hashlib
import sys
from pathlib import Path

ROOT = Path('/app')
SUITE = ROOT / 'backend/scripts/run_hero_skill_kit_validator_suite.py'

EXPECTED_INVARIANTS = {
    'backend/battle_engine.py': '151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env': 'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py': '893f244d85fd45cbe825996463995293',
    'frontend/app/artifacts-preview.tsx': '0e75c94e00899af773dbc9faf7326a15',
    'frontend/app/artifacts.tsx': '8849e21c44207fc1d0074cae2cdc6879',
    'frontend/app/(tabs)/gacha.tsx': 'f68b9239cec04ea54879f0be381e772a',
}


def md5(rel):
    return hashlib.md5((ROOT / rel).read_bytes()).hexdigest()


def main():
    src = SUITE.read_text()
    # Sentinels
    assert 'PUBLIC_SYNC_TAG: suite_runner_live_signoff_v3_force_resnapshot_2026_05_27' in src, \
        "top sentinel v3 missing"
    assert 'PUBLIC_SYNC_TAG_RESYNC_v4: suite_runner_live_signoff_v4_force_resnapshot_after_stale_push_175' in src, \
        "top sentinel v4 missing"
    assert 'STAGE_7_LIVE_ACTIVATION_SIGNOFF_REGISTRATION_SENTINEL' in src, \
        "inline sentinel STAGE_7 missing"
    assert 'STAGE_7_LIVE_ACTIVATION_SIGNOFF_REGISTRATION_RESYNC_v4' in src, \
        "inline sentinel RESYNC_v4 missing"

    # Registration tuple present exactly once
    needle = "'PROJECT-ARTIFACT-INVENTORY-LIVE-ACTIVATION-SIGNOFF'"
    count = src.count(needle)
    assert count == 1, f"registration tuple count expected 1, got {count}"
    assert "'validate_project_artifact_inventory_live_activation_signoff_v1.py'" in src

    # Stage 6 sentinel preserved
    assert 'STAGE_6_GATED_IMPORT_REGISTRATION_SENTINEL' in src
    assert "'PROJECT-ARTIFACT-INVENTORY-GATED-IMPORT'" in src

    # AST parseable
    ast.parse(src)

    # MD5 invariants
    for rel, expected in EXPECTED_INVARIANTS.items():
        actual = md5(rel)
        assert actual == expected, f"MD5 drift on {rel}: expected {expected}, got {actual}"

    # Track JSONs exist
    for fname in ('sync_fix_audit_v1.json', 'sync_fix_patch_v1.json', 'sync_fix_validation_v1.json'):
        p = ROOT / 'data/design/artifacts/live_signoff_sync_fix' / fname
        assert p.is_file(), f"missing tracking JSON {fname}"

    # patch_v1.json: confirm runtime_routes_modified=false, env_modified=false, db_modified=false
    import json
    patch = json.loads((ROOT / 'data/design/artifacts/live_signoff_sync_fix/sync_fix_patch_v1.json').read_text())
    assert patch['runtime_routes_modified'] is False
    assert patch['env_modified'] is False
    assert patch['db_modified'] is False
    assert patch['existing_tuple_duplicated'] is False
    assert patch['required_validator_block_touched'] is False

    print('[PASS] PROJECT_ARTIFACT_LIVE_SIGNOFF_SUITE_RUNNER_SYNC_FIX master validator')
    return 0


if __name__ == '__main__':
    sys.exit(main())
