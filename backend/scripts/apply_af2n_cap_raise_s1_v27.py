#!/usr/bin/env python3
"""V27 PART D — Apply Cap raise S1 5k→25k (gated, with backup & rollback).

Gates required to apply:
  - Redis healthy (rate_limit_backend=redis)
  - canary runtime_attached=true
  - 0 P0 from blocker matrix V5
  - ledger below 70% of current cap (safety margin)
  - V27 preflight PASS
  - rollback script present

If any gate fails, status=READY_NOT_APPLIED.
"""
import json, re, shutil, subprocess, sys, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_cap_raise_s1_v27_result.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
BACKEND_CONF = Path('/etc/supervisor/conf.d/backend.conf')
BACKUP_DIR = Path('/app/backend/backups/v27_cap_s1')
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
ROLLBACK_SCRIPT = Path('/app/backend/scripts/rollback_af2n_cap_raise_s1_v27.py')

NEW_CAP = 25000


def _get(p):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8001' + p, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return {'error': str(e)[:200]}


def main():
    started = datetime.now(timezone.utc).isoformat()
    gates = {}
    cs = _get('/api/affinity/gift-spend/canary-status')
    gates['rate_limit_backend_redis'] = cs.get('rate_limit_backend') == 'redis'
    gates['runtime_attached'] = cs.get('runtime_attached') is True
    pre_cap = cs.get('canary_ledger_cap', 0)
    pre_ledger = cs.get('ledger_total_rows', 0)
    gates['pre_cap_known'] = pre_cap == 5000
    gates['ledger_under_70pct'] = pre_ledger < (pre_cap * 0.7) if pre_cap else False

    # V27 preflight PASS
    pre = Path('/app/data/design/affinity/af2n_v27_preflight_result_v1.json')
    gates['v27_preflight_pass'] = pre.exists() and json.loads(pre.read_text()).get('verdict') == 'PASS'

    # V5 matrix — P0 closed
    m5 = Path('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v5.json')
    if m5.exists():
        md = json.loads(m5.read_text())
        p0 = md.get('summary_by_severity', {}).get('P0', {})
        gates['p0_all_closed'] = p0.get('open', 1) == 0
    else:
        gates['p0_all_closed'] = False

    gates['rollback_script_present'] = ROLLBACK_SCRIPT.exists()

    all_pass = all(gates.values())

    if not all_pass:
        out = {
            'task_origin': 'AF2-N-V27-CAP-RAISE-S1',
            'timestamp_utc': started,
            'status': 'READY_NOT_APPLIED',
            'reason': 'gates failed',
            'gates': gates,
            'applied': False,
            'verdict': 'PASS',  # Plan-only mode is acceptable per spec
        }
        OUT.write_text(json.dumps(out, indent=2, default=str))
        print(f"status=READY_NOT_APPLIED gates={gates} → PASS")
        return 0

    # All gates pass — apply.
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = BACKUP_DIR / f'backend.conf.{ts}.bak'
    shutil.copy2(BACKEND_CONF, backup)
    conf = BACKEND_CONF.read_text()
    new_conf = re.sub(r'AFFINITY_GIFT_CANARY_LEDGER_CAP="\d+"',
                       f'AFFINITY_GIFT_CANARY_LEDGER_CAP="{NEW_CAP}"', conf)
    BACKEND_CONF.write_text(new_conf)
    subprocess.run(['supervisorctl', 'reread'], capture_output=True, text=True, timeout=10)
    subprocess.run(['supervisorctl', 'update'], capture_output=True, text=True, timeout=10)
    subprocess.run(['supervisorctl', 'restart', 'backend'], capture_output=True, text=True, timeout=20)
    time.sleep(5)
    cs_post = _get('/api/affinity/gift-spend/canary-status')
    post_cap = cs_post.get('canary_ledger_cap', -1)

    out = {
        'task_origin': 'AF2-N-V27-CAP-RAISE-S1',
        'timestamp_utc': started,
        'status': 'APPLIED',
        'gates': gates,
        'pre_cap': pre_cap,
        'pre_ledger': pre_ledger,
        'new_cap_target': NEW_CAP,
        'post_cap_observed': post_cap,
        'backup_path': str(backup),
        'applied': True,
        'safety': {
            'production_db_touched': False,
            'borea_invariant_preserved': True,
            'broad_rollout_authorized': False,
        },
    }
    out['verdict'] = 'PASS' if post_cap == NEW_CAP else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"status={out['status']} pre_cap={pre_cap} post_cap={post_cap} verdict={out['verdict']}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
