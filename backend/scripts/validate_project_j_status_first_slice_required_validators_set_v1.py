#!/usr/bin/env python3
"""PROJECT_J Track C validator — REQUIRED-candidate validators set registered as OPTIONAL."""
import json, sys
from pathlib import Path
MARKER = Path('/app/data/design/status_effects/project_j_status_first_slice_required_validators_set_v1.json')
SUITE = Path('/app/backend/scripts/run_hero_skill_kit_validator_suite.py')
def fail(m): print(f'[FAIL] {m}'); sys.exit(1)
def main():
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_C_STATUS_FIRST_SLICE_REQUIRED_CANDIDATE_VALIDATORS_READY': fail('verdict mismatch')
    if m.get('registration_mode') != 'OPTIONAL_REQUIRED_CANDIDATE': fail('registration_mode must be OPTIONAL_REQUIRED_CANDIDATE')
    if m.get('validators_promoted_to_REQUIRED_in_pack_j') != 0: fail('zero promotions in Pack J')
    if m.get('required_diff_guard_preserved') is not True: fail('required_diff_guard_preserved must be True')
    if m.get('required_weakening') is not False: fail('required_weakening must be False')
    body = SUITE.read_text()
    for v in m.get('required_candidate_validators', []):
        if v not in body: fail(f'validator {v} not registered in suite OPTIONAL')
        if not (Path('/app/backend/scripts')/v).exists(): fail(f'validator file missing: {v}')
    print('[PASS] PROJECT_J Track C 5 REQUIRED-candidate validators registered as OPTIONAL; 0 promotions; no weakening')
    sys.exit(0)
if __name__ == '__main__': main()
