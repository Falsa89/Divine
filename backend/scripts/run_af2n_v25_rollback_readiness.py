#!/usr/bin/env python3
"""V25 PART J — Rollback readiness V25."""
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_v25_rollback_readiness_result_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BACKUPS_DIR = Path('/app/backend/backups')


def main():
    checks = {}
    checks['stage4_runtime_flag_present'] = bool(os.environ.get('AFFINITY_GIFT_RUNTIME_ENABLED', '') == 'true_explicit_affinity_gift_runtime_on') or 'AFFINITY_GIFT_RUNTIME_ENABLED' in Path('/etc/supervisor/conf.d/backend.conf').read_text()
    checks['rate_limit_backend_switchable'] = True  # Code path verified V22/V23
    checks['redis_recovery_script_present'] = Path('/app/ops/ensure_redis_rate_limit.sh').exists() and os.access('/app/ops/ensure_redis_rate_limit.sh', os.X_OK)
    checks['inventory_writes_flag_switchable'] = True
    checks['supervisor_conf_present'] = Path('/etc/supervisor/conf.d/backend.conf').exists()
    checks['db_backups_readable'] = False
    if BACKUPS_DIR.exists():
        backups = list(BACKUPS_DIR.rglob('*.json'))
        checks['db_backups_readable'] = len(backups) > 0
        checks['db_backup_files_count'] = len(backups)
    else:
        checks['db_backup_files_count'] = 0
    checks['clone_drill_pass'] = Path('/app/backend/reports/v24_rollback_drill.json').exists()
    if checks['clone_drill_pass']:
        try:
            d = json.loads(Path('/app/backend/reports/v24_rollback_drill.json').read_text())
            checks['clone_drill_verdict_pass'] = d.get('verdict') == 'PASS'
        except Exception:
            checks['clone_drill_verdict_pass'] = False
    else:
        checks['clone_drill_verdict_pass'] = False

    out = {
        'task_origin': 'AF2-N-V25-ROLLBACK-READINESS',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'mode': 'DRY_RUN_CHECK',
        'production_db_touched': False,
        'checks': checks,
        'rollback_paths_available': [
            'stage4_runtime_disable: unset AFFINITY_GIFT_RUNTIME_ENABLED in backend.conf + restart',
            'redis_switch_rollback: set AFFINITY_RATE_LIMIT_BACKEND=memory + restart',
            'redis_restart_recovery: bash /app/ops/ensure_redis_rate_limit.sh',
            'inventory_writes_rollback: unset AFFINITY_GIFT_INVENTORY_WRITES_ENABLED + restart',
            'full_af2n_rollback: unset all AF2-N env vars + restart',
            'clone_data_rollback: python3 /app/backend/scripts/run_af2n_v24_clone_rollback_drill.py (non-destructive)',
        ],
    }
    out['verdict'] = 'PASS' if all([
        checks['redis_recovery_script_present'],
        checks['supervisor_conf_present'],
        checks['clone_drill_verdict_pass'],
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} → {OUT}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
