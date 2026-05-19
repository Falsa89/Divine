#!/usr/bin/env python3
"""V25 PART L — ULTRA-COMBO V25 composite validator.

Runs all V25 PART validators and aggregates results.
"""
import subprocess, sys
from pathlib import Path

VALIDATORS = [
    ('AF2-N-V25-PREFLIGHT',                   'validate_af2n_v25_preflight.py'),
    ('AF2-N-V25-REDIS-OPS-RECOVERY',          'validate_redis_rate_limit_ops_recovery.py'),
    ('AF2-N-V25-REDIS-RESTART-DRILL',         'validate_redis_rate_limit_restart_drill_v25.py'),
    ('AF2-N-V25-FAIL-OPEN-ALERTING-CONTRACT', 'validate_af2n_fail_open_alerting_contract.py'),
    ('AF2-N-V25-ALERTING-READONLY-STATUS',    'audit_af2n_alerting_readonly_status.py'),
    ('AF2-N-V25-SUPPORT-RUNBOOK',             'validate_af2n_stage4_support_runbook_v25.py'),
    ('AF2-N-V25-ECONOMY-STRESS-10X',          'validate_af2n_economy_stress_10x_simulation_v25.py'),
    ('AF2-N-V25-BLOCKER-MATRIX-V4',           'validate_af2n_broad_rollout_blocker_matrix_v4.py'),
    ('AF2-N-V25-OBSERVATION-WINDOW',          'validate_af2n_stage4_observation_window_v25.py'),
    ('AF2-N-V25-UI-SAFETY',                   'audit_affinity_gifts_public_preview_v25_safety.py'),
    ('AF2-N-V25-ROLLBACK-READINESS',          'validate_af2n_v25_rollback_readiness.py'),
    ('AF2-N-V25-SAFETY-ROLLUP-T',             'validate_collection_affinity_runtime_activation_rollup_v20.py'),
]
ROOT = Path('/app/backend/scripts')


def main():
    fails = []
    passes = []
    for label, script in VALIDATORS:
        path = ROOT / script
        if not path.exists():
            fails.append(f'missing:{label}:{script}')
            continue
        r = subprocess.run(['python3', str(path)], capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            passes.append(label)
        else:
            fails.append(f'fail:{label}:exit={r.returncode}:{(r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout or r.stderr) else ""}')
    print(f"ULTRA-COMBO-V25 {'PASS' if not fails else 'FAIL'} passes={len(passes)} fails={len(fails)}")
    for p in passes: print(f'  ✓ {p}')
    for f in fails: print(f'  ✗ {f}')
    return 0 if not fails else 2


if __name__ == '__main__':
    sys.exit(main())
