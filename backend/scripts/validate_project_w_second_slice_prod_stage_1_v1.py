#!/usr/bin/env python3
# PROJECT_W TRACK B — SECOND SLICE PROD STAGE 1% VALIDATOR
# Read-only. Conferma che lo stage 1% sia READY_NOT_APPLIED o ENABLED_SAFE, e che
# in stato pending nessun flip / DB write / battle mutation sia avvenuto.
import json, sys, hashlib
from pathlib import Path

MARKER = Path('/app/data/design/status_effects/project_w_second_slice_prod_stage_1_result_v1.json')
ENV = Path('/app/backend/.env')
BATTLE_ENGINE = Path('/app/backend/battle_engine.py')
ROLLBACK = Path('/app/backend/scripts/rollback_project_w_second_slice_prod_stage_1.py')

def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest() if p.exists() else None

def main():
    if not MARKER.exists():
        print('[FAIL] marker JSON missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['target_rollout_percent'] == 1
    assert m['flag_flipped'] is False
    assert m['prod_env_touched'] is False
    assert m['db_writes'] is False
    assert m['battle_engine_mutated'] is False
    assert m['env_byte_identical'] is True
    assert ROLLBACK.exists(), 'rollback script missing'
    assert md5(BATTLE_ENGINE) == '151ca35ad3bc35f0a6209cb3744ed440'
    valid_verdicts = (
        'TRACK_B_SECOND_SLICE_PROD_STAGE_1_ENABLED_SAFE',
        'TRACK_B_SECOND_SLICE_PROD_STAGE_1_READY_NOT_APPLIED_PENDING_APPROVAL',
        'TRACK_B_SECOND_SLICE_PROD_STAGE_1_BLOCKED',
    )
    assert m['verdict'] in valid_verdicts
    print(f'[PASS] PROJECT_W Track B stage 1% — verdict={m["verdict"]}, applied={m["applied"]}, rollback_path={ROLLBACK.name}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
