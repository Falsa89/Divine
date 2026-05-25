#!/usr/bin/env python3
# PROJECT_SERVER_PROFILES_LEGACY_DEPRECATION_AUDIT / TRACK G
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_smoke_regression_requirements_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_G_SERVER_PROFILES_SMOKE_AND_REGRESSION_REQUIREMENTS_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['global_markers']['TRACK_G_SERVER_PROFILES_SMOKE_REGRESSION_REQUIREMENTS_APPROVAL'] == 'true'
    sr = d['smoke_requirements']
    for cat in ['legacy_endpoint_smoke','new_endpoint_smoke','ui_smoke','flag_state_smoke','db_state_smoke','rollback_validation','mobile_qa']:
        assert cat in sr and isinstance(sr[cat], list) and len(sr[cat]) >= 1, f'category {cat} missing/empty'
    forb = d['forbidden_smoke_actions']
    assert any('flag flip' in f for f in forb)
    assert any('DB write' in f for f in forb)
    assert any('mobile QA' in f or 'screenshot' in f for f in forb)
    fut = d['regression_validators_to_add_in_future_packs']
    assert isinstance(fut, list) and len(fut) >= 2
    print(f"[PASS] SP Track G smoke/regression requirements READY \u2014 categories={len(sr)}, future_validators={len(fut)}")
    return 0
if __name__ == '__main__': sys.exit(main())
