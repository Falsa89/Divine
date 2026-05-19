#!/usr/bin/env python3
"""V25 PART B — Audit Redis rate-limit ops recovery scripts."""
import json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/redis_rate_limit_ops_recovery_result_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)

REQUIRED = {
    '/app/ops/ensure_redis_rate_limit.sh': ['idempotent', 'redis-cli ping', 'supervisorctl', 'apt-get install'],
    '/app/ops/restore_redis_supervisor_service.sh': ['redis.conf', 'supervisorctl', 'reread'],
    '/app/ops/README_REDIS_RATE_LIMIT_RECOVERY.md': ['Idempotent', 'BLK-B-01', 'Safety'],
}


def main():
    report = {
        'task_origin': 'AF2-N-V25-REDIS-OPS-RECOVERY-AUDIT',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'files': {},
        'live_recovery_test': {},
    }
    fails = []
    for f, tokens in REQUIRED.items():
        p = Path(f)
        exists = p.exists()
        executable = exists and (os.access(f, os.X_OK) or f.endswith('.md'))
        txt = p.read_text() if exists else ''
        missing_tokens = [t for t in tokens if t.lower() not in txt.lower()]
        report['files'][f] = {
            'exists': exists,
            'executable_or_md': executable,
            'size_bytes': len(txt),
            'missing_tokens': missing_tokens,
        }
        if not exists: fails.append(f'missing:{f}')
        if not executable: fails.append(f'not_exec:{f}')
        if missing_tokens: fails.append(f'tokens:{f}:{missing_tokens}')

    # Live recovery: run ensure_redis_rate_limit.sh and check it exits 0
    try:
        r = subprocess.run(['bash', '/app/ops/ensure_redis_rate_limit.sh'],
                            capture_output=True, text=True, timeout=30)
        report['live_recovery_test'] = {
            'returncode': r.returncode,
            'stdout_tail': r.stdout.strip().splitlines()[-6:],
            'stderr_tail': r.stderr.strip().splitlines()[-6:],
            'idempotent_ok': r.returncode == 0,
        }
        if r.returncode != 0:
            fails.append(f'recovery_rc={r.returncode}')
    except Exception as e:
        fails.append(f'recovery_exc:{e}')

    report['fails'] = fails
    report['verdict'] = 'PASS' if not fails else 'FAIL'
    OUT.write_text(json.dumps(report, indent=2, default=str))
    print(f"verdict={report['verdict']} → {OUT}")
    return 0 if not fails else 2


if __name__ == '__main__':
    sys.exit(main())
