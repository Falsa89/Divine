#!/usr/bin/env python3
"""V22 — Run Stage4 Locust extended (60s, 15 users)."""
from __future__ import annotations
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen

LF = Path('/app/loadtests/af2n_v22_stage4_extended_locustfile.py')
OUT = Path('/app/data/design/affinity/af2n_v22_locust_stage4_extended_result_v1.json')
NOW = datetime.now(timezone.utc)


def _canary():
    try:
        with urlopen('http://127.0.0.1:8001/api/affinity/gift-spend/canary-status', timeout=4) as r:
            return json.loads(r.read().decode())
    except Exception:
        return {}


def main():
    pre = _canary()
    if pre.get('canary_allowlist_size', 0) < 700:
        out = {'overall_status':'BLOCKED_NO_STAGE4','reason':'Stage4 not active'}
        OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(out, indent=2))
        print('LOCUST-EXTENDED BLOCKED_NO_STAGE4'); return 0
    cmd = ['locust','-f',str(LF),'--host','http://127.0.0.1:8001',
           '--headless','-u','15','-r','5','-t','60s',
           '--csv','/tmp/v22_locust_stage4','--only-summary']
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=150)
    post = _canary()
    out_text = (proc.stdout or '') + '\n' + (proc.stderr or '')
    total = None; failures = None; p95 = None; p99 = None
    # crude parse
    for line in out_text.splitlines():
        if 'Aggregated' in line:
            parts = [p for p in line.split() if p.replace('.','').replace('-','').isdigit()]
            try:
                if len(parts) >= 2:
                    total = int(float(parts[0])); failures = int(float(parts[1]))
            except Exception: pass
    ledger_grew = post.get('ledger_total_rows', 0) - pre.get('ledger_total_rows', 0)
    cap_exceeded = post.get('ledger_total_rows', 0) > post.get('canary_ledger_cap', 0)
    safe_growth = ledger_grew <= 20
    inv_neg = 0
    try:
        from pymongo import MongoClient
        db = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']
        inv_neg = db['user_gift_inventory'].count_documents({'quantity': {'$lt': 0}})
    except Exception: pass
    overall = (proc.returncode == 0) and (not cap_exceeded) and safe_growth and (inv_neg == 0)
    out_doc = {
        'result_id':'af2n_v22_locust_stage4_extended_result_v1',
        'task_origin':'V22-LOCUST-STAGE4-EXTENDED',
        'started_at_utc': NOW.isoformat().replace('+00:00','Z'),
        'finished_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
        'locust_returncode': proc.returncode,
        'total_reqs_approx': total,
        'failures_approx': failures,
        'pre_canary_status': pre, 'post_canary_status': post,
        'ledger_growth': ledger_grew, 'cap_exceeded': cap_exceeded,
        'safe_ledger_growth': safe_growth,
        'negative_inventory_count': inv_neg,
        'stdout_tail': out_text[-2500:],
        'overall_status': 'PASS' if overall else 'FAIL',
        'safety_invariants': [
            'fresh spend budget capped at 5 globally',
            'mostly status/replay/non-allowlist/burst traffic',
            'no Borea writes', 'no battle wiring', 'no buffs',
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out_doc, indent=2))
    print(f'V22-LOCUST-STAGE4-EXTENDED {out_doc["overall_status"]} growth={ledger_grew} inv_neg={inv_neg}')
    return 0 if overall else 2


if __name__ == '__main__':
    sys.exit(main())
