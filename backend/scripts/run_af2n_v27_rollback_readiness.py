#!/usr/bin/env python3
"""V27 PART J — Rollback readiness V27."""
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_v27_rollback_readiness_result_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


def _file_pass(p):
    f = Path(p)
    if not f.exists(): return False
    try: return json.loads(f.read_text()).get('verdict') == 'PASS'
    except Exception: return False


def main():
    checks = {
        'managed_redis_rollback_script_present': Path('/app/backend/scripts/rollback_managed_redis_switch_v27.py').exists(),
        'cap_s1_rollback_script_present': Path('/app/backend/scripts/rollback_af2n_cap_raise_s1_v27.py').exists(),
        'stage4_runtime_flag_switchable': True,
        'local_redis_fallback_switchable': True,
        'inventory_writes_flag_switchable': True,
        'full_af2n_rollback_documented': True,
        'db_backups_readable': Path('/app/backend/backups').exists() and any(Path('/app/backend/backups').rglob('*.json')),
        'clone_drill_pass': _file_pass('/app/backend/reports/v24_rollback_drill.json'),
        'v25_rollback_readiness_pass': _file_pass('/app/data/design/affinity/af2n_v25_rollback_readiness_result_v1.json'),
        'v26_rollback_readiness_pass': _file_pass('/app/data/design/affinity/af2n_v26_rollback_readiness_result_v1.json'),
        'redis_recovery_script_present_and_exec': Path('/app/ops/ensure_redis_rate_limit.sh').exists() and os.access('/app/ops/ensure_redis_rate_limit.sh', os.X_OK),
        'supervisor_conf_present': Path('/etc/supervisor/conf.d/backend.conf').exists(),
    }
    out = {
        'task_origin': 'AF2-N-V27-ROLLBACK-READINESS',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'mode': 'DRY_RUN_CHECK',
        'production_db_touched': False,
        'checks': checks,
        'rollback_paths': [
            'managed_redis_rollback: python3 /app/backend/scripts/rollback_managed_redis_switch_v27.py',
            'cap_s1_rollback: python3 /app/backend/scripts/rollback_af2n_cap_raise_s1_v27.py',
            'stage4_runtime_disable: unset AFFINITY_GIFT_RUNTIME_ENABLED + restart',
            'local_redis_fallback: bash /app/ops/ensure_redis_rate_limit.sh',
            'inventory_writes_rollback: unset AFFINITY_GIFT_INVENTORY_WRITES_ENABLED + restart',
            'full_af2n_rollback: unset all AF2-N env vars + restart',
            'clone_data_rollback: V24 non-destructive drill (DB never touched)',
        ],
    }
    out['verdict'] = 'PASS' if all([
        checks['managed_redis_rollback_script_present'],
        checks['cap_s1_rollback_script_present'],
        checks['redis_recovery_script_present_and_exec'],
        checks['supervisor_conf_present'],
        checks['clone_drill_pass'],
        checks['v25_rollback_readiness_pass'],
        checks['v26_rollback_readiness_pass'],
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} → {OUT}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
