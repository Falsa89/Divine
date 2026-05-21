#!/usr/bin/env python3
"""V30 PART N — Composite ULTRA-COMBO V30."""
import subprocess, sys
from pathlib import Path

VALIDATORS = [
    ('AF2-N-V30-PREFLIGHT',                        'validate_af2n_v30_preflight.py'),
    ('AF2-N-V30-STAGE4-SOAK',                      'validate_af2n_stage4_soak_v30.py'),
    ('AF2-N-V30-CAP-RAISE-S2',                     'validate_af2n_cap_raise_s2_v30.py'),
    ('AF2-N-V30-STRESS-10X',                       'validate_af2n_stress_10x_v30.py'),
    ('AF2-N-V30-MANAGED-REDIS-PROBE',              'validate_managed_redis_envaware_v30.py'),
    ('AF2-N-V30-ALERTING-PROBE',                   'validate_alerting_envaware_v30.py'),
    ('AF2-N-V30-OBSERVABILITY-DASHBOARD-SPEC',     'validate_af2n_observability_dashboard_spec.py'),
    ('AF2-N-V30-INVENTORY-DELTA-AUDIT',            'validate_affinity_inventory_delta_consistency_v30.py'),
    ('AF2-N-V30-BROAD-ROLLOUT-SIGNOFF-V8',         'validate_af2n_broad_rollout_signoff_package_v8.py'),
    ('AF2-N-V30-BLOCKER-MATRIX-V9',                'validate_af2n_broad_rollout_blocker_matrix_v9.py'),
    ('AF2-N-V30-UI-SAFETY',                        'audit_affinity_gifts_public_preview_v30_safety.py'),
    ('AF2-N-V30-ROLLBACK-READINESS',               'validate_af2n_v30_rollback_readiness.py'),
    ('AF2-N-V30-SAFETY-ROLLUP-Y',                  'validate_collection_affinity_runtime_activation_rollup_v25.py'),
]
ROOT = Path('/app/backend/scripts')


def main():
    passes=[]; fails=[]
    for label, script in VALIDATORS:
        p=ROOT/script
        if not p.exists(): fails.append(f'missing:{label}'); continue
        r=subprocess.run(['python3', str(p)], capture_output=True, text=True, timeout=60)
        if r.returncode==0: passes.append(label)
        else:
            tail=((r.stdout or '')+(r.stderr or '')).strip().splitlines()
            fails.append(f'fail:{label}:{tail[-1] if tail else ""}')
    print(f"ULTRA-COMBO-V30 {'PASS' if not fails else 'FAIL'} passes={len(passes)} fails={len(fails)}")
    for x in passes: print(f'  ✓ {x}')
    for x in fails: print(f'  ✗ {x}')
    return 0 if not fails else 2


if __name__ == '__main__': sys.exit(main())
