#!/usr/bin/env python3
"""V28 PART L — Composite ULTRA-COMBO V28."""
import subprocess, sys
from pathlib import Path

VALIDATORS = [
    ('AF2-N-V28-PREFLIGHT',                    'validate_af2n_v28_preflight.py'),
    ('AF2-N-V28-INVENTORY-SCOPE-S1',           'validate_af2n_inventory_scope_s1_v28.py'),
    ('AF2-N-V28-SCOPE-S1-OBSERVATION',         'validate_af2n_scope_s1_observation_v28.py'),
    ('AF2-N-V28-STRESS-5X',                    'validate_af2n_stress_5x_v28.py'),
    ('AF2-N-V28-INVENTORY-DELTA-AUDIT',        'validate_affinity_inventory_delta_consistency_v28.py'),
    ('AF2-N-V28-MANAGED-REDIS-PROBE',          'validate_managed_redis_v28_probe.py'),
    ('AF2-N-V28-ALERTING-LIVE-PROBE',          'validate_alerting_live_v28_probe.py'),
    ('AF2-N-V28-BLOCKER-MATRIX-V7',            'validate_af2n_broad_rollout_blocker_matrix_v7.py'),
    ('AF2-N-V28-UI-SAFETY',                    'audit_affinity_gifts_public_preview_v28_safety.py'),
    ('AF2-N-V28-ROLLBACK-READINESS',           'validate_af2n_v28_rollback_readiness.py'),
    ('AF2-N-V28-SAFETY-ROLLUP-W',              'validate_collection_affinity_runtime_activation_rollup_v23.py'),
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
    print(f"ULTRA-COMBO-V28 {'PASS' if not fails else 'FAIL'} passes={len(passes)} fails={len(fails)}")
    for p in passes: print(f'  ✓ {p}')
    for f in fails: print(f'  ✗ {f}')
    return 0 if not fails else 2


if __name__ == '__main__':
    sys.exit(main())
