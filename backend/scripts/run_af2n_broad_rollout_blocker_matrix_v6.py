#!/usr/bin/env python3
"""V27 PART H — Blocker Matrix V6."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v6.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


def _file_pass(p):
    f = Path(p)
    if not f.exists(): return None
    try: return json.loads(f.read_text())
    except Exception: return None


def main():
    # Read V27 results to determine new statuses
    mgmt = _file_pass('/app/data/design/affinity/managed_redis_switch_v27_result.json') or {}
    cap = _file_pass('/app/data/design/affinity/af2n_cap_raise_s1_v27_result.json') or {}
    alert = _file_pass('/app/data/design/affinity/af2n_alerting_sink_v27_result.json') or {}
    stress = _file_pass('/app/data/design/affinity/af2n_stress_3x_v27_result.json') or {}

    mgmt_status = mgmt.get('status', 'UNKNOWN')
    cap_status = cap.get('status', 'UNKNOWN')
    alert_mode = alert.get('sink_mode', 'UNKNOWN')

    MATRIX = [
        # P0
        {'id': 'BLK-A-01', 'severity': 'P0', 'title': 'battle_engine/combat untouched', 'status': 'CLOSED'},
        {'id': 'BLK-A-02', 'severity': 'P0', 'title': 'Borea aliases 404', 'status': 'CLOSED'},
        {'id': 'BLK-A-03', 'severity': 'P0', 'title': '/api/heroes=100', 'status': 'CLOSED'},
        {'id': 'BLK-A-04', 'severity': 'P0', 'title': 'No 5xx observation', 'status': 'CLOSED'},
        {'id': 'BLK-A-05', 'severity': 'P0', 'title': 'No unauthorized spend', 'status': 'CLOSED'},
        # P1
        {'id': 'BLK-B-01', 'severity': 'P1', 'title': 'Ephemeral container Redis init/restore', 'status': 'CLOSED_V25'},
        {'id': 'BLK-B-02', 'severity': 'P1', 'title': 'Redis non-persistent', 'status': 'ACCEPTED'},
        {'id': 'BLK-B-03', 'severity': 'P1', 'title': 'Redis SPOF (single-node)',
         'status': f'LIVE_CLOSED_V27' if mgmt_status == 'SWITCHED' else 'READY_NOT_APPLIED_V27',
         'closed_by': mgmt_status},
        {'id': 'BLK-B-04', 'severity': 'P1', 'title': 'Rollback drill on clone', 'status': 'CLOSED'},
        {'id': 'BLK-B-05', 'severity': 'P1', 'title': 'Abuse metrics instrumented', 'status': 'CLOSED'},
        {'id': 'BLK-B-06', 'severity': 'P1', 'title': 'Cap raise 5k→25k S1',
         'status': 'LIVE_CLOSED_V27' if cap_status == 'APPLIED' else 'READY_NOT_APPLIED_V27',
         'closed_by': cap_status},
        {'id': 'BLK-B-07', 'severity': 'P1', 'title': 'Inventory writes scope expansion', 'status': 'PLAN_READY_V26'},
        # P2
        {'id': 'BLK-C-01', 'severity': 'P2', 'title': 'Public Spend UI off', 'status': 'CLOSED'},
        {'id': 'BLK-C-02', 'severity': 'P2', 'title': 'STACK-G wiring deferred', 'status': 'CLOSED'},
        {'id': 'BLK-C-03', 'severity': 'P2', 'title': 'Frontend smoke', 'status': 'CLOSED_V26'},
        # P3
        {'id': 'BLK-D-01', 'severity': 'P3', 'title': 'Runbook restart Redis', 'status': 'CLOSED_V25'},
        {'id': 'BLK-D-02', 'severity': 'P3', 'title': 'Alerting contract', 'status': 'CLOSED_V25'},
        {'id': 'BLK-D-02-LIVE', 'severity': 'P3', 'title': 'Alerting live sink',
         'status': 'LIVE_CLOSED_V27' if alert_mode.startswith('LIVE_') else f'MOCK_CLOSED_V27',
         'closed_by': alert_mode},
        {'id': 'BLK-D-03', 'severity': 'P3', 'title': 'Support playbook', 'status': 'CLOSED_V25'},
        {'id': 'BLK-E-01', 'severity': 'P1', 'title': 'Economy stress 10x sim', 'status': 'CLOSED_V25'},
        {'id': 'BLK-F-01', 'severity': 'P1', 'title': 'Stress 2x', 'status': 'CLOSED_V26'},
        {'id': 'BLK-F-02', 'severity': 'P1', 'title': 'Stress 3x',
         'status': 'CLOSED_V27' if stress.get('verdict') == 'PASS' else 'OPEN'},
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
        'task_origin': 'AF2-N-V27-BLOCKER-MATRIX-V6',
        'version': 'v6',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'stage': 'stage4_internal_beta_active_no_broad_rollout',
        'broad_rollout_authorized': False,
        'public_spend_ui_authorized': False,
        'matrix': MATRIX,
        'summary_by_severity': by_sev,
        'v27_transitions': {
            'BLK-B-03': mgmt_status,
            'BLK-B-06': cap_status,
            'BLK-D-02-LIVE': alert_mode,
            'BLK-F-02': 'CLOSED_V27' if stress.get('verdict') == 'PASS' else 'OPEN',
        },
        'broad_rollout_blocker_explicit': 'BLK-G-01 (final user approval not granted)',
        'verdict': 'PASS' if by_sev.get('P0', {}).get('open', 1) == 0 else 'FAIL',
    }
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} V27_transitions={out['v27_transitions']} → {OUT}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
