#!/usr/bin/env python3
"""V29 PART M — Composite ULTRA-COMBO V29."""
import subprocess, sys
from pathlib import Path

VALIDATORS = [
    ('AF2-N-V29-PREFLIGHT',                       'validate_af2n_v29_preflight.py'),
    ('AF2-N-V29-V28-SCHEMA-FIX-REGRESSION',       'validate_af2n_v28_schema_fix_regression_v29.py'),
    ('AF2-N-V29-MANAGED-REDIS-PROBE',             'validate_managed_redis_envaware_v29.py'),
    ('AF2-N-V29-ALERTING-PROBE',                  'validate_alerting_envaware_v29.py'),
    ('AF2-N-V29-SCOPE-S1-EXTENDED-MONITORING',    'validate_af2n_scope_s1_extended_monitoring_v29.py'),
    ('AF2-N-V29-STRESS-8X',                       'validate_af2n_stress_8x_v29.py'),
    ('AF2-N-V29-INVENTORY-DELTA-AUDIT',           'validate_affinity_inventory_delta_consistency_v29.py'),
    ('AF2-N-V29-BROAD-ROLLOUT-SIGNOFF-V7',        'validate_af2n_broad_rollout_signoff_package_v7.py'),
    ('AF2-N-V29-BLOCKER-MATRIX-V8',               'validate_af2n_broad_rollout_blocker_matrix_v8.py'),
    ('AF2-N-V29-UI-SAFETY',                       'audit_affinity_gifts_public_preview_v29_safety.py'),
    ('AF2-N-V29-ROLLBACK-READINESS',              'validate_af2n_v29_rollback_readiness.py'),
    ('AF2-N-V29-SAFETY-ROLLUP-X',                 'validate_collection_affinity_runtime_activation_rollup_v24.py'),
]
ROOT = Path('/app/backend/scripts')


def main():
    passes = []; fails = []
    for label, script in VALIDATORS:
        path = ROOT / script
        if not path.exists():
            fails.append(f'missing:{label}'); continue
        r = subprocess.run(['python3', str(path)], capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            passes.append(label)
        else:
            tail = ((r.stdout or '') + (r.stderr or '')).strip().splitlines()
            fails.append(f'fail:{label}:{tail[-1] if tail else ""}')
    print(f"ULTRA-COMBO-V29 {'PASS' if not fails else 'FAIL'} passes={len(passes)} fails={len(fails)}")
    for p in passes: print(f'  ✓ {p}')
    for f in fails: print(f'  ✗ {f}')
    return 0 if not fails else 2


if __name__ == '__main__':
    sys.exit(main())
