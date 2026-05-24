#!/usr/bin/env python3
# PROJECT_W TRACK F — SECOND SLICE PROD FINAL NO-LEAK / LOAD / ROLLBACK VALIDATOR
import json, sys, hashlib
from pathlib import Path
MARKER = Path('/app/data/design/status_effects/project_w_second_slice_prod_final_validation_v1.json')
BATTLE_ENGINE = Path('/app/backend/battle_engine.py')
ENV = Path('/app/backend/.env')

def md5(p): return hashlib.md5(p.read_bytes()).hexdigest() if p.exists() else None

def main():
    if not MARKER.exists():
        print('[FAIL] marker JSON missing'); return 1
    m = json.loads(MARKER.read_text())
    assert m['db_writes'] is False
    assert m['battle_engine_mutated'] is False
    assert m['hidden_failures'] is False
    assert m['env_byte_identical'] is True
    assert m['final_state_after_validation'] in ('FLAG_OFF', 'FLAG_ON_KEEP_ON')
    if not m['keep_on_marker_present']:
        assert m['final_state_after_validation'] == 'FLAG_OFF', 'final must be OFF without keep-on marker'
    assert md5(BATTLE_ENGINE) == '151ca35ad3bc35f0a6209cb3744ed440'
    assert md5(ENV) == 'ff60bbb79efa329b71aa8ed351ea89b3'
    assert m['verdict'] == 'TRACK_F_SECOND_SLICE_PROD_FINAL_NO_LEAK_LOAD_ROLLBACK_READY'
    print(f'[PASS] PROJECT_W Track F final no-leak/load/rollback — highest_stage={m["highest_stage_reached_percent"]}%, final={m["final_state_after_validation"]}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
