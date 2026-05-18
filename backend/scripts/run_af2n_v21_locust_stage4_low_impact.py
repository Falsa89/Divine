#!/usr/bin/env python3
"""V21 — Run Stage4 Locust low-impact for ~30s.

Writes result JSON. Non-destructive.
"""
from __future__ import annotations
import json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

LOCUSTFILE = Path('/app/loadtests/af2n_v21_stage4_locustfile.py')
OUT = Path('/app/data/design/affinity/af2n_v21_locust_stage4_result_v1.json')
NOW = datetime.now(timezone.utc)


def _canary():
    try:
        with urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=4) as r:
            return json.loads(r.read().decode())
    except Exception:
        return {}


def main():
    pre = _canary()
    stage4_active = pre.get('canary_allowlist_size', 0) >= 700 and pre.get('canary_ledger_cap', 0) >= 5000
    cmd = [
        'locust', '-f', str(LOCUSTFILE),
        '--host', 'http://127.0.0.1:8001',
        '--headless', '-u', '4', '-r', '2', '-t', '30s',
        '--csv', '/tmp/v21_locust_stage4', '--only-summary',
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    post = _canary()
    # parse summary from stdout/stderr
    out_text = (proc.stdout or '') + '\n' + (proc.stderr or '')
    rps = None; failures = None; total = None
    for line in out_text.splitlines():
        if 'Aggregated' in line:
            parts = line.split()
            # locust format: Name # reqs # fails | Avg Min Max | Median req/s failures/s
            try:
                # take numeric tokens
                nums = [p for p in parts if p.replace('.', '').replace('-', '').isdigit()]
                if len(nums) >= 2:
                    total = int(float(nums[0]))
                    failures = int(float(nums[1]))
            except Exception:
                pass
    # invariants
    ledger_grew = post.get('ledger_total_rows', 0) - pre.get('ledger_total_rows', 0)
    cap_exceeded = post.get('ledger_total_rows', 0) > post.get('canary_ledger_cap', 0)
    safe_ledger_growth = ledger_grew <= 15  # very low-impact threshold (cap is 5000)
    overall = (not cap_exceeded) and safe_ledger_growth and proc.returncode == 0
    out_doc = {
        'result_id': 'af2n_v21_locust_stage4_result_v1',
        'task_origin': 'V21-LOCUST-STAGE4-LOW-IMPACT',
        'started_at_utc': NOW.isoformat().replace('+00:00', 'Z'),
        'finished_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'mode': 'stage4' if stage4_active else 'stage3_fallback',
        'locust_returncode': proc.returncode,
        'locust_summary_total_reqs': total,
        'locust_summary_failures': failures,
        'pre_canary_status': pre,
        'post_canary_status': post,
        'ledger_growth': ledger_grew,
        'cap_exceeded': cap_exceeded,
        'safe_ledger_growth': safe_ledger_growth,
        'stdout_tail': out_text[-2000:],
        'overall_status': 'PASS' if overall else 'FAIL',
        'safety_invariants': [
            'fresh spend budget capped at 5 globally',
            'mostly status / replay / non-allowlist traffic',
            'no Borea writes', 'no battle wiring', 'no buffs'
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out_doc, indent=2))
    print(f'V21-LOCUST-STAGE4 {out_doc["overall_status"]} growth={ledger_grew} cap_exceeded={cap_exceeded}')
    return 0 if overall else 2


if __name__ == '__main__':
    sys.exit(main())
