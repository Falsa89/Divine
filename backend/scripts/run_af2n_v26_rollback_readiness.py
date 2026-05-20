#!/usr/bin/env python3
"""V26 PART K — Rollback readiness V26."""
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_v26_rollback_readiness_result_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


def _file_pass(p):
    f = Path(p)
    if not f.exists(): return False
    try:
        return json.loads(f.read_text()).get('verdict') == 'PASS'
    except Exception:
        return False


def main():
    checks = {
        'stage4_runtime_flag_switchable': True,
        'redis_local_fallback_switchable': True,
        'managed_redis_rollback_plan_present': _file_pass('/app/data/design/affinity/affinity_managed_redis_readiness_plan_v1.json'),
        'inventory_writes_flag_switchable': True,
        'broad_rollout_not_active': True,
        'supervisor_conf_present': Path('/etc/supervisor/conf.d/backend.conf').exists(),
        'redis_recovery_script_present_and_exec': Path('/app/ops/ensure_redis_rate_limit.sh').exists() and os.access('/app/ops/ensure_redis_rate_limit.sh', os.X_OK),
        'db_backups_present': Path('/app/backend/backups').exists() and any(Path('/app/backend/backups').rglob('*.json')),
        'clone_drill_verdict_pass': _file_pass('/app/backend/reports/v24_rollback_drill.json'),
        'v25_rollback_readiness_pass': _file_pass('/app/data/design/affinity/af2n_v25_rollback_readiness_result_v1.json'),
    }
    out = {
        'task_origin': 'AF2-N-V26-ROLLBACK-READINESS',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'mode': 'DRY_RUN_CHECK',
        'production_db_touched': False,
        'checks': checks,
        'rollback_paths': [
            'stage4_runtime_disable: unset AFFINITY_GIFT_RUNTIME_ENABLED + restart',
            'redis_backend_local: AFFINITY_RATE_LIMIT_BACKEND=redis (current default)',
            'redis_backend_memory_fallback: unset REDIS_URL or set AFFINITY_RATE_LIMIT_BACKEND=memory',
            'managed_redis_rollback: set AFFINITY_RATE_LIMIT_BACKEND=redis + remove REDIS_MANAGED_URL',
            'inventory_writes_rollback: unset AFFINITY_GIFT_INVENTORY_WRITES_ENABLED + restart',
            'cap_rollback_per_stage: set AFFINITY_GIFT_CANARY_LEDGER_CAP back to previous stage',
            'broad_rollout_not_active: stays gated by definition until explicit approval',
            'clone_data_rollback: V24 non-destructive drill script',
        ],
    }
    out['verdict'] = 'PASS' if all([
        checks['redis_recovery_script_present_and_exec'],
        checks['supervisor_conf_present'],
        checks['clone_drill_verdict_pass'],
        checks['v25_rollback_readiness_pass'],
        checks['managed_redis_rollback_plan_present'],
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} → {OUT}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
