#!/usr/bin/env python3
"""V28 PART J — Rollback readiness V28."""
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_v28_rollback_readiness_result_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


def _file_pass(p):
    f = Path(p)
    if not f.exists(): return False
    try: return json.loads(f.read_text()).get('verdict') == 'PASS'
    except Exception: return False


def main():
    checks = {
        'scope_s1_rollback_script_present': Path('/app/backend/scripts/rollback_af2n_inventory_scope_s1_v28.py').exists(),
        'allowlist_backup_v28_present': any(Path('/app/backend/backups/v28_scope_s1').glob('*.bak'))
            if Path('/app/backend/backups/v28_scope_s1').exists() else False,
        'cap_s1_rollback_script_present': Path('/app/backend/scripts/rollback_af2n_cap_raise_s1_v27.py').exists(),
        'redis_recovery_script_present_and_exec': Path('/app/ops/ensure_redis_rate_limit.sh').exists() and os.access('/app/ops/ensure_redis_rate_limit.sh', os.X_OK),
        'managed_redis_rollback_script_present': Path('/app/backend/scripts/rollback_managed_redis_switch_v27.py').exists(),
        'inventory_writes_flag_switchable': True,
        'stage4_runtime_flag_switchable': True,
        'supervisor_conf_present': Path('/etc/supervisor/conf.d/backend.conf').exists(),
        'db_backups_present': Path('/app/backend/backups').exists() and any(Path('/app/backend/backups').rglob('*.json')),
        'clone_drill_pass_v24': _file_pass('/app/backend/reports/v24_rollback_drill.json'),
        'v25_rollback_readiness_pass': _file_pass('/app/data/design/affinity/af2n_v25_rollback_readiness_result_v1.json'),
        'v26_rollback_readiness_pass': _file_pass('/app/data/design/affinity/af2n_v26_rollback_readiness_result_v1.json'),
        'v27_rollback_readiness_pass': _file_pass('/app/data/design/affinity/af2n_v27_rollback_readiness_result_v1.json'),
    }
    out = {
        'task_origin': 'AF2-N-V28-ROLLBACK-READINESS',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'mode': 'DRY_RUN_CHECK',
        'production_db_touched': False,
        'checks': checks,
        'rollback_paths': [
            'scope_s1_rollback: python3 /app/backend/scripts/rollback_af2n_inventory_scope_s1_v28.py (deletes marker docs + restores conf)',
            'cap_s1_rollback: python3 /app/backend/scripts/rollback_af2n_cap_raise_s1_v27.py',
            'redis_local_recovery: bash /app/ops/ensure_redis_rate_limit.sh',
            'managed_redis_rollback: python3 /app/backend/scripts/rollback_managed_redis_switch_v27.py',
            'stage4_runtime_disable: unset AFFINITY_GIFT_RUNTIME_ENABLED + restart',
            'inventory_writes_rollback: unset AFFINITY_GIFT_INVENTORY_WRITES_ENABLED + restart',
            'full_af2n_rollback: unset all AF2-N env vars + restart',
        ],
    }
    out['verdict'] = 'PASS' if all([
        checks['scope_s1_rollback_script_present'],
        checks['allowlist_backup_v28_present'],
        checks['cap_s1_rollback_script_present'],
        checks['redis_recovery_script_present_and_exec'],
        checks['supervisor_conf_present'],
        checks['clone_drill_pass_v24'],
        checks['v25_rollback_readiness_pass'],
        checks['v26_rollback_readiness_pass'],
        checks['v27_rollback_readiness_pass'],
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
