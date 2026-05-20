#!/usr/bin/env python3
"""V27 PART B — Apply Managed Redis switch (gated, with backup & rollback).

Only runs if probe PASS. Edits /etc/supervisor/conf.d/backend.conf with backup.
The switch is NEVER attempted if REDIS_MANAGED_URL is absent.
"""
import json, os, re, shutil, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/managed_redis_switch_v27_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BACKEND_CONF = Path('/etc/supervisor/conf.d/backend.conf')
BACKUP_DIR = Path('/app/backend/backups/v27_switch')
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
PROBE_RESULT = Path('/app/data/design/affinity/managed_redis_probe_v27_result.json')


def main():
    started = datetime.now(timezone.utc).isoformat()
    url = os.environ.get('REDIS_MANAGED_URL', '').strip()
    if not url:
        OUT.write_text(json.dumps({
            'task_origin': 'AF2-N-V27-MANAGED-REDIS-SWITCH',
            'timestamp_utc': started,
            'status': 'READY_NOT_APPLIED',
            'reason': 'REDIS_MANAGED_URL absent',
            'switch_applied': False,
            'verdict': 'PASS',
        }, indent=2))
        print('status=READY_NOT_APPLIED → PASS (no env)')
        return 0

    if not PROBE_RESULT.exists():
        OUT.write_text(json.dumps({
            'status': 'PROBE_MISSING',
            'verdict': 'FAIL',
            'reason': 'probe result missing; run probe_managed_redis_v27.py first',
        }, indent=2))
        print('FAIL: probe missing'); return 2

    probe = json.loads(PROBE_RESULT.read_text())
    if probe.get('verdict') != 'PASS' or probe.get('status') != 'CONNECTED':
        OUT.write_text(json.dumps({
            'status': 'PROBE_NOT_PASS',
            'verdict': 'FAIL',
            'probe_status': probe.get('status'),
        }, indent=2))
        print('FAIL: probe not PASS'); return 2

    # Backup
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = BACKUP_DIR / f'backend.conf.{ts}.bak'
    shutil.copy2(BACKEND_CONF, backup)
    conf = BACKEND_CONF.read_text()

    # Replace or add REDIS_URL and AFFINITY_RATE_LIMIT_BACKEND
    new_conf = conf
    if 'REDIS_URL=' in new_conf:
        new_conf = re.sub(r'REDIS_URL="[^"]*"', f'REDIS_URL="{url}"', new_conf)
    else:
        new_conf = new_conf.replace('environment=', f'environment=REDIS_URL="{url}",', 1)

    if 'AFFINITY_RATE_LIMIT_BACKEND=' in new_conf:
        new_conf = re.sub(r'AFFINITY_RATE_LIMIT_BACKEND="[^"]*"',
                           'AFFINITY_RATE_LIMIT_BACKEND="redis"', new_conf)
    BACKEND_CONF.write_text(new_conf)

    # Restart backend
    subprocess.run(['supervisorctl', 'reread'], capture_output=True, text=True, timeout=10)
    subprocess.run(['supervisorctl', 'update'], capture_output=True, text=True, timeout=10)
    subprocess.run(['supervisorctl', 'restart', 'backend'], capture_output=True, text=True, timeout=20)

    # Wait + verify
    import time, urllib.request
    time.sleep(5)
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=5) as r:
            cs = json.loads(r.read().decode())
    except Exception as e:
        cs = {'error': str(e)[:200]}

    out = {
        'task_origin': 'AF2-N-V27-MANAGED-REDIS-SWITCH',
        'timestamp_utc': started,
        'status': 'SWITCHED',
        'switch_applied': True,
        'host_redacted': probe.get('host_redacted'),
        'backup_path': str(backup),
        'canary_post_switch': {
            'rate_limit_backend': cs.get('rate_limit_backend'),
            'runtime_attached': cs.get('runtime_attached'),
        },
        'verdict': 'PASS' if cs.get('rate_limit_backend') == 'redis' else 'FAIL',
    }
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"status=SWITCHED verdict={out['verdict']}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
