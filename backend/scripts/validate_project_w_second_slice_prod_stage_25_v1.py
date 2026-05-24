#!/usr/bin/env python3
# PROJECT_W TRACK D — SECOND SLICE PROD STAGE 25% VALIDATOR
import json, sys, hashlib
from pathlib import Path
MARKER = Path('/app/data/design/status_effects/project_w_second_slice_prod_stage_25_result_v1.json')
BATTLE_ENGINE = Path('/app/backend/battle_engine.py')
ROLLBACK = Path('/app/backend/scripts/rollback_project_w_second_slice_prod_stage_25.py')

def md5(p): return hashlib.md5(p.read_bytes()).hexdigest() if p.exists() else None

def main():
    if not MARKER.exists():
        print('[FAIL] marker JSON missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['target_rollout_percent'] == 25
    assert m['flag_flipped'] is False
    assert m['prod_env_touched'] is False
    assert m['db_writes'] is False
    assert m['battle_engine_mutated'] is False
    assert m['env_byte_identical'] is True
    assert ROLLBACK.exists()
    assert md5(BATTLE_ENGINE) == '151ca35ad3bc35f0a6209cb3744ed440'
    valid = (
        'TRACK_D_SECOND_SLICE_PROD_STAGE_25_ENABLED_SAFE',
        'TRACK_D_SECOND_SLICE_PROD_STAGE_25_READY_NOT_APPLIED_PENDING_APPROVAL',
        'TRACK_D_SECOND_SLICE_PROD_STAGE_25_BLOCKED',
    )
    assert m['verdict'] in valid
    if m['verdict'] == 'TRACK_D_SECOND_SLICE_PROD_STAGE_25_ENABLED_SAFE':
        assert m['escalation_dependency_met'] is True
    print(f'[PASS] PROJECT_W Track D stage 25% — verdict={m["verdict"]}, escalation_dep_met={m["escalation_dependency_met"]}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
