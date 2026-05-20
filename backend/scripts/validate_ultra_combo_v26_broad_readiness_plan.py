#!/usr/bin/env python3
"""V26 PART M — ULTRA-COMBO V26 composite validator."""
import subprocess, sys
from pathlib import Path

VALIDATORS = [
    ('AF2-N-V26-PREFLIGHT',                     'validate_af2n_v26_preflight.py'),
    ('AF2-N-V26-MANAGED-REDIS-READINESS',       'validate_affinity_managed_redis_readiness.py'),
    ('AF2-N-V26-CAP-RAISE-PLAN',                'validate_af2n_cap_raise_plan.py'),
    ('AF2-N-V26-INVENTORY-SCOPE-PLAN',          'validate_af2n_inventory_scope_expansion_plan.py'),
    ('AF2-N-V26-BROAD-ROLLOUT-SIGNOFF-V6',      'validate_af2n_broad_rollout_signoff_package_v6.py'),
    ('AF2-N-V26-ALERTING-INTEGRATION-PREP',     'audit_af2n_alerting_integration_prep.py'),
    ('AF2-N-V26-FRONTEND-SMOKE',                'audit_affinity_gifts_frontend_smoke_v26.py'),
    ('AF2-N-V26-STRESS-2X',                     'validate_af2n_stress_2x_v26.py'),
    ('AF2-N-V26-BLOCKER-MATRIX-V5',             'validate_af2n_broad_rollout_blocker_matrix_v5.py'),
    ('AF2-N-V26-OBSERVATION-WINDOW',            'validate_af2n_stage4_observation_window_v26.py'),
    ('AF2-N-V26-ROLLBACK-READINESS',            'validate_af2n_v26_rollback_readiness.py'),
    ('AF2-N-V26-SAFETY-ROLLUP-U',               'validate_collection_affinity_runtime_activation_rollup_v21.py'),
]
ROOT = Path('/app/backend/scripts')


def main():
    passes = []
    fails = []
    for label, script in VALIDATORS:
        path = ROOT / script
        if not path.exists():
            fails.append(f'missing:{label}')
            continue
        r = subprocess.run(['python3', str(path)], capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            passes.append(label)
        else:
            tail = ((r.stdout or '') + (r.stderr or '')).strip().splitlines()
            fails.append(f'fail:{label}:{tail[-1] if tail else ""}')
    print(f"ULTRA-COMBO-V26 {'PASS' if not fails else 'FAIL'} passes={len(passes)} fails={len(fails)}")
    for p in passes: print(f'  ✓ {p}')
    for f in fails: print(f'  ✗ {f}')
    return 0 if not fails else 2


if __name__ == '__main__':
    sys.exit(main())
