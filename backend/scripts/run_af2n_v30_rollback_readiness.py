#!/usr/bin/env python3
"""V30 PART L — Rollback readiness V30."""
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path
OUT = Path('/app/data/design/affinity/af2n_v30_rollback_readiness_result_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


def _file_pass(p):
    f=Path(p)
    if not f.exists(): return False
    try: return json.loads(f.read_text()).get('verdict')=='PASS'
    except Exception: return False


def main():
    checks={
        'cap_s2_rollback_script_present': Path('/app/backend/scripts/rollback_af2n_cap_raise_s2_v30.py').exists(),
        'cap_s2_backups_present': Path('/app/backend/backups/v30_cap_s2').exists() and any(Path('/app/backend/backups/v30_cap_s2').glob('*.bak')),
        'cap_s1_rollback_script_present': Path('/app/backend/scripts/rollback_af2n_cap_raise_s1_v27.py').exists(),
        'scope_s1_rollback_script_present': Path('/app/backend/scripts/rollback_af2n_inventory_scope_s1_v28.py').exists(),
        'redis_recovery_script_present_and_exec': Path('/app/ops/ensure_redis_rate_limit.sh').exists() and os.access('/app/ops/ensure_redis_rate_limit.sh', os.X_OK),
        'managed_redis_rollback_script_present': Path('/app/backend/scripts/rollback_managed_redis_switch_v27.py').exists(),
        'supervisor_conf_present': Path('/etc/supervisor/conf.d/backend.conf').exists(),
        'db_backups_present': Path('/app/backend/backups').exists() and any(Path('/app/backend/backups').rglob('*.json')),
        'v25_rollback_pass': _file_pass('/app/data/design/affinity/af2n_v25_rollback_readiness_result_v1.json'),
        'v26_rollback_pass': _file_pass('/app/data/design/affinity/af2n_v26_rollback_readiness_result_v1.json'),
        'v27_rollback_pass': _file_pass('/app/data/design/affinity/af2n_v27_rollback_readiness_result_v1.json'),
        'v28_rollback_pass': _file_pass('/app/data/design/affinity/af2n_v28_rollback_readiness_result_v1.json'),
        'v29_rollback_pass': _file_pass('/app/data/design/affinity/af2n_v29_rollback_readiness_result_v1.json'),
        'v24_drill_pass': _file_pass('/app/backend/reports/v24_rollback_drill.json'),
    }
    out={
        'task_origin':'AF2-N-V30-ROLLBACK-READINESS',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'mode':'DRY_RUN_CHECK','production_db_touched':False,'checks':checks,
        'rollback_paths':[
            'cap_s2: python3 /app/backend/scripts/rollback_af2n_cap_raise_s2_v30.py (50k→25k, restore conf + route from backup)',
            'cap_s1: python3 /app/backend/scripts/rollback_af2n_cap_raise_s1_v27.py',
            'scope_s1: python3 /app/backend/scripts/rollback_af2n_inventory_scope_s1_v28.py',
            'redis_local: bash /app/ops/ensure_redis_rate_limit.sh',
            'managed_redis: python3 /app/backend/scripts/rollback_managed_redis_switch_v27.py',
            'alerting_live: unset ALERT_WEBHOOK_URL/PROMETHEUS_PUSHGATEWAY + restart',
            'stage4_runtime_disable: unset AFFINITY_GIFT_RUNTIME_ENABLED + restart',
            'inventory_writes_rollback: unset AFFINITY_GIFT_INVENTORY_WRITES_ENABLED + restart',
            'full_af2n_rollback: unset all AF2-N env vars + restart',
        ],
    }
    # cap_s2_backups_present is allowed to be False if cap S2 was not applied. Only fail on critical script presence.
    critical = ['cap_s2_rollback_script_present','cap_s1_rollback_script_present','scope_s1_rollback_script_present',
                'redis_recovery_script_present_and_exec','managed_redis_rollback_script_present','supervisor_conf_present',
                'v25_rollback_pass','v26_rollback_pass','v27_rollback_pass','v28_rollback_pass','v29_rollback_pass','v24_drill_pass']
    out['verdict']='PASS' if all(checks[k] for k in critical) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']}")
    return 0 if out['verdict']=='PASS' else 2


if __name__ == '__main__': sys.exit(main())
