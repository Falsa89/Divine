#!/usr/bin/env python3
"""V27 PART L — Composite ULTRA-COMBO V27."""
import subprocess, sys
from pathlib import Path

VALIDATORS = [
    ('AF2-N-V27-PREFLIGHT',                    'validate_af2n_v27_preflight.py'),
    ('AF2-N-V27-MANAGED-REDIS-SWITCH',         'validate_managed_redis_switch_v27.py'),
    ('AF2-N-V27-ALERTING-SINK',                'validate_af2n_alerting_sink_v27.py'),
    ('AF2-N-V27-CAP-RAISE-S1',                 'validate_af2n_cap_raise_s1_v27.py'),
    ('AF2-N-V27-STAGE4-OBSERVATION',           'validate_af2n_stage4_observation_v27.py'),
    ('AF2-N-V27-STRESS-3X',                    'validate_af2n_stress_3x_v27.py'),
    ('AF2-N-V27-INVENTORY-DELTA-AUDIT',        'validate_affinity_inventory_delta_consistency_v27.py'),
    ('AF2-N-V27-BLOCKER-MATRIX-V6',            'validate_af2n_broad_rollout_blocker_matrix_v6.py'),
    ('AF2-N-V27-UI-SAFETY',                    'audit_affinity_gifts_public_preview_v27_safety.py'),
    ('AF2-N-V27-ROLLBACK-READINESS',           'validate_af2n_v27_rollback_readiness.py'),
    ('AF2-N-V27-SAFETY-ROLLUP-V',              'validate_collection_affinity_runtime_activation_rollup_v22.py'),
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
    print(f"ULTRA-COMBO-V27 {'PASS' if not fails else 'FAIL'} passes={len(passes)} fails={len(fails)}")
    for p in passes: print(f'  ✓ {p}')
    for f in fails: print(f'  ✗ {f}')
    return 0 if not fails else 2


if __name__ == '__main__':
    sys.exit(main())
