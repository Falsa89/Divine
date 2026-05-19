#!/usr/bin/env python3
"""V23 — Validate abuse monitoring prep plan."""
from __future__ import annotations
import json, sys
from pathlib import Path

P = Path('/app/data/design/affinity/af2n_v23_abuse_monitoring_prep_plan_v1.json')
REQ_METRICS = [
    'af2_gift_spend_total','af2_gift_spend_5xx_total','af2_gift_spend_borea_404_total',
    'af2_gift_spend_unauthorized_success_total','af2_ratelimit_429_total',
    'af2_ratelimit_redis_fail_open_total','af2_ledger_total_rows',
    'af2_inventory_negative_count','af2_inventory_affinity_delta_mismatch_total','af2_gift_spend_latency_ms',
]
REQ_ALERT_IDS = ['AF2-A-001','AF2-A-002','AF2-A-003','AF2-A-004','AF2-A-005','AF2-A-006','AF2-A-007','AF2-A-008']


def main():
    if not P.exists(): print(f'FAIL: missing {P}'); return 2
    d = json.loads(P.read_text())
    fails = []
    if d.get('design_only') is not True: fails.append('not_design_only')
    if d.get('dashboards_live') is not False: fails.append('dashboards_live_true')
    if d.get('alerts_live') is not False: fails.append('alerts_live_true')
    metrics = {m.get('metric') for m in d.get('metrics', [])}
    missing_metrics = set(REQ_METRICS) - metrics
    if missing_metrics: fails.append(f'missing_metrics:{sorted(missing_metrics)}')
    alert_ids = {a.get('alert_id') for a in d.get('alerts', [])}
    missing_alerts = set(REQ_ALERT_IDS) - alert_ids
    if missing_alerts: fails.append(f'missing_alerts:{sorted(missing_alerts)}')
    if d.get('broad_rollout_prerequisite') is not True: fails.append('not_marked_prereq')
    if fails:
        for f in fails: print(f'FAIL: {f}')
        return 2
    print('PASS: AF2-N-V23-ABUSE-MONITORING-PREP'); return 0


if __name__ == '__main__':
    sys.exit(main())
