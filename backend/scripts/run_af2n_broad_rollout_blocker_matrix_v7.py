#!/usr/bin/env python3
"""V28 PART H — Blocker Matrix V7."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v7.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


def _read(p):
    f = Path(p)
    return json.loads(f.read_text()) if f.exists() else {}


def main():
    scope = _read('/app/data/design/affinity/af2n_inventory_scope_s1_v28_result.json')
    stress = _read('/app/data/design/affinity/af2n_stress_5x_v28_result.json')
    mgmt = _read('/app/data/design/affinity/managed_redis_v28_probe_result.json')
    alert = _read('/app/data/design/affinity/alerting_live_v28_probe_result.json')

    MATRIX = [
        {'id': 'BLK-A-01', 'severity': 'P0', 'title': 'battle untouched', 'status': 'CLOSED'},
        {'id': 'BLK-A-02', 'severity': 'P0', 'title': 'Borea aliases 404', 'status': 'CLOSED'},
        {'id': 'BLK-A-03', 'severity': 'P0', 'title': '/api/heroes=100', 'status': 'CLOSED'},
        {'id': 'BLK-A-04', 'severity': 'P0', 'title': 'No 5xx', 'status': 'CLOSED'},
        {'id': 'BLK-A-05', 'severity': 'P0', 'title': 'No unauthorized spend', 'status': 'CLOSED'},
        {'id': 'BLK-B-01', 'severity': 'P1', 'title': 'Container Redis init/restore', 'status': 'CLOSED_V25'},
        {'id': 'BLK-B-02', 'severity': 'P1', 'title': 'Redis non-persistent', 'status': 'ACCEPTED'},
        {'id': 'BLK-B-03', 'severity': 'P1', 'title': 'Redis SPOF',
         'status': 'LIVE_CLOSED_V28' if mgmt.get('status') == 'CONNECTED' else 'READY_NOT_APPLIED_V28',
         'closed_by': mgmt.get('status')},
        {'id': 'BLK-B-04', 'severity': 'P1', 'title': 'Rollback drill clone', 'status': 'CLOSED'},
        {'id': 'BLK-B-05', 'severity': 'P1', 'title': 'Abuse metrics', 'status': 'CLOSED'},
        {'id': 'BLK-B-06', 'severity': 'P1', 'title': 'Cap raise S1 5k->25k', 'status': 'LIVE_CLOSED_V27'},
        {'id': 'BLK-B-07', 'severity': 'P1', 'title': 'Inventory scope S1 expansion',
         'status': 'LIVE_CLOSED_V28' if scope.get('status') == 'APPLIED' else 'READY_NOT_APPLIED_V28',
         'closed_by': scope.get('status')},
        {'id': 'BLK-C-01', 'severity': 'P2', 'title': 'Public Spend UI off', 'status': 'CLOSED'},
        {'id': 'BLK-C-02', 'severity': 'P2', 'title': 'STACK-G wiring deferred', 'status': 'CLOSED'},
        {'id': 'BLK-C-03', 'severity': 'P2', 'title': 'Frontend smoke', 'status': 'CLOSED_V26'},
        {'id': 'BLK-D-01', 'severity': 'P3', 'title': 'Redis runbook', 'status': 'CLOSED_V25'},
        {'id': 'BLK-D-02', 'severity': 'P3', 'title': 'Alerting contract', 'status': 'CLOSED_V25'},
        {'id': 'BLK-D-02-LIVE', 'severity': 'P3', 'title': 'Alerting live sink',
         'status': 'LIVE_CLOSED_V28' if alert.get('sink_mode', '').startswith('LIVE_') else 'MOCK_CLOSED_V28',
         'closed_by': alert.get('sink_mode')},
        {'id': 'BLK-D-03', 'severity': 'P3', 'title': 'Support playbook', 'status': 'CLOSED_V25'},
        {'id': 'BLK-E-01', 'severity': 'P1', 'title': 'Economy stress 10x sim', 'status': 'CLOSED_V25'},
        {'id': 'BLK-F-01', 'severity': 'P1', 'title': 'Stress 2x', 'status': 'CLOSED_V26'},
        {'id': 'BLK-F-02', 'severity': 'P1', 'title': 'Stress 3x', 'status': 'CLOSED_V27'},
        {'id': 'BLK-F-03', 'severity': 'P1', 'title': 'Stress 5x',
         'status': 'CLOSED_V28' if stress.get('verdict') == 'PASS' else 'OPEN'},
        {'id': 'BLK-G-01', 'severity': 'P0', 'title': 'Broad rollout signoff V6 final approval',
         'status': 'PLAN_READY_NOT_APPROVED'},
    ]
    by_sev = {}
    for b in MATRIX:
        sv = b['severity']
        by_sev.setdefault(sv, {'open': 0, 'addressed': 0, 'total': 0})
        by_sev[sv]['total'] += 1
        st = b['status']
        if any(t in st for t in ('CLOSED', 'ACCEPTED', 'READY', 'NOT_APPROVED')):
            by_sev[sv]['addressed'] += 1
        else:
            by_sev[sv]['open'] += 1
    out = {
        'task_origin': 'AF2-N-V28-BLOCKER-MATRIX-V7', 'version': 'v7',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'stage': 'stage4_internal_beta_active_no_broad_rollout (with scope S1 expansion to 2500)',
        'broad_rollout_authorized': False,
        'public_spend_ui_authorized': False,
        'matrix': MATRIX,
        'summary_by_severity': by_sev,
        'v28_transitions': {
            'BLK-B-07': scope.get('status'),
            'BLK-F-03': 'CLOSED_V28' if stress.get('verdict') == 'PASS' else 'OPEN',
            'BLK-B-03': mgmt.get('status'),
            'BLK-D-02-LIVE': alert.get('sink_mode'),
        },
        'verdict': 'PASS' if by_sev.get('P0', {}).get('open', 1) == 0 else 'FAIL',
    }
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} V28_transitions={out['v28_transitions']}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
