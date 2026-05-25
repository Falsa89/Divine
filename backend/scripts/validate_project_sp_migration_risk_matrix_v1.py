#!/usr/bin/env python3
# PROJECT_SERVER_PROFILES_LEGACY_DEPRECATION_AUDIT / TRACK D
import json, sys
from pathlib import Path
P = Path('/app/data/design/server_profiles/project_sp_migration_risk_matrix_v1.json')
def main():
    d = json.loads(P.read_text())
    assert d['verdict'] == 'TRACK_D_SERVER_PROFILE_MIGRATION_RISK_MATRIX_READY'
    assert d['audit_mode'] == 'audit_only'
    assert d['db_writes'] == 0
    assert d['global_markers']['TRACK_D_SERVER_PROFILE_MIGRATION_RISK_MATRIX_APPROVAL'] == 'true'
    m = d['risk_matrix']
    assert isinstance(m, list) and len(m) >= 5
    # Each item must have severity LOW/MEDIUM/HIGH/CRITICAL
    sevs = [r['severity'] for r in m]
    for s in sevs:
        assert s in ('LOW','MEDIUM','HIGH','CRITICAL')
    # At least one CRITICAL: orphan users
    assert any(r['severity'] == 'CRITICAL' for r in m)
    ds = d['dual_write_strategy_recommended']
    for k in ['phase_0_safe_now','phase_1_seed','phase_2_dual_write','phase_3_read_through','phase_4_cutover','phase_5_deprecate']:
        assert k in ds, f'missing phase {k}'
    assert d['lock_recommendation_during_transition'] is True
    print(f"[PASS] SP Track D migration risk matrix READY \u2014 risks={len(m)}, critical={sum(1 for r in m if r['severity']=='CRITICAL')}")
    return 0
if __name__ == '__main__': sys.exit(main())
