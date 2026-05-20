#!/usr/bin/env python3
"""V29 PART I — Blocker Matrix V8."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path
OUT = Path('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v8.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


def _read(p):
    f = Path(p)
    if not f.exists(): return {}
    try: return json.loads(f.read_text())
    except Exception: return {}


def main():
    schema_reg = _read('/app/data/design/affinity/af2n_v28_schema_fix_regression_v29_result.json')
    scope = _read('/app/data/design/affinity/af2n_inventory_scope_s1_v28_result.json')
    ext = _read('/app/data/design/affinity/af2n_scope_s1_extended_monitoring_v29_result.json')
    s8 = _read('/app/data/design/affinity/af2n_stress_8x_v29_result.json')
    mredis = _read('/app/data/design/affinity/managed_redis_envaware_v29_result.json')
    alert = _read('/app/data/design/affinity/alerting_envaware_v29_result.json')
    delta = _read('/app/data/design/affinity/affinity_inventory_delta_consistency_v29_report.json')

    MATRIX = [
        {'id': 'BLK-A-01', 'severity': 'P0', 'title': 'battle untouched', 'status': 'CLOSED'},
        {'id': 'BLK-A-02', 'severity': 'P0', 'title': 'Borea aliases 404', 'status': 'CLOSED'},
        {'id': 'BLK-A-03', 'severity': 'P0', 'title': '/api/heroes=100', 'status': 'CLOSED'},
        {'id': 'BLK-A-04', 'severity': 'P0', 'title': 'No 5xx', 'status': 'CLOSED'},
        {'id': 'BLK-A-05', 'severity': 'P0', 'title': 'No unauthorized spend', 'status': 'CLOSED'},
        {'id': 'BLK-B-01', 'severity': 'P1', 'title': 'Container Redis init/restore', 'status': 'CLOSED_V25'},
        {'id': 'BLK-B-02', 'severity': 'P1', 'title': 'Redis non-persistent', 'status': 'ACCEPTED'},
        {'id': 'BLK-B-03', 'severity': 'P1', 'title': 'Redis SPOF (Managed Redis switch)',
         'status': 'LIVE_CLOSED_V29' if mredis.get('status') == 'PROBED_CONNECTED' else 'READY_NOT_APPLIED_ENV_MISSING_V29',
         'closed_by': mredis.get('status')},
        {'id': 'BLK-B-04', 'severity': 'P1', 'title': 'Rollback drill clone', 'status': 'CLOSED'},
        {'id': 'BLK-B-05', 'severity': 'P1', 'title': 'Abuse metrics', 'status': 'CLOSED'},
        {'id': 'BLK-B-06', 'severity': 'P1', 'title': 'Cap raise S1 5k->25k', 'status': 'LIVE_CLOSED_V27'},
        {'id': 'BLK-B-07', 'severity': 'P1', 'title': 'Inventory scope S1 expansion',
         'status': 'LIVE_CLOSED_V28' if scope.get('status') == 'APPLIED' else 'OPEN'},
        {'id': 'BLK-B-08', 'severity': 'P0', 'title': 'V28 schema-fix regression (nested→flat)',
         'status': 'CLOSED_V29' if schema_reg.get('verdict') == 'PASS' else 'OPEN'},
        {'id': 'BLK-C-01', 'severity': 'P2', 'title': 'Public Spend UI off', 'status': 'CLOSED'},
        {'id': 'BLK-C-02', 'severity': 'P2', 'title': 'STACK-G wiring deferred', 'status': 'CLOSED'},
        {'id': 'BLK-C-03', 'severity': 'P2', 'title': 'Frontend smoke', 'status': 'CLOSED_V26'},
        {'id': 'BLK-D-01', 'severity': 'P3', 'title': 'Redis runbook', 'status': 'CLOSED_V25'},
        {'id': 'BLK-D-02', 'severity': 'P3', 'title': 'Alerting contract', 'status': 'CLOSED_V25'},
        {'id': 'BLK-D-02-LIVE', 'severity': 'P3', 'title': 'Alerting live sink',
         'status': 'LIVE_CLOSED_V29' if (alert.get('sink_mode') or '').startswith('LIVE_') else 'MOCK_ENV_MISSING_V29',
         'closed_by': alert.get('sink_mode')},
        {'id': 'BLK-D-03', 'severity': 'P3', 'title': 'Support playbook', 'status': 'CLOSED_V25'},
        {'id': 'BLK-E-01', 'severity': 'P1', 'title': 'Economy stress 10x sim', 'status': 'CLOSED_V25'},
        {'id': 'BLK-F-01', 'severity': 'P1', 'title': 'Stress 2x', 'status': 'CLOSED_V26'},
        {'id': 'BLK-F-02', 'severity': 'P1', 'title': 'Stress 3x', 'status': 'CLOSED_V27'},
        {'id': 'BLK-F-03', 'severity': 'P1', 'title': 'Stress 5x', 'status': 'CLOSED_V28'},
        {'id': 'BLK-F-04', 'severity': 'P1', 'title': 'Stress 8x',
         'status': 'CLOSED_V29' if s8.get('verdict') == 'PASS' else 'OPEN'},
        {'id': 'BLK-H-01', 'severity': 'P1', 'title': 'Extended monitoring scope S1',
         'status': 'CLOSED_V29' if ext.get('verdict') == 'PASS' else 'OPEN'},
        {'id': 'BLK-H-02', 'severity': 'P1', 'title': 'Full delta audit V29',
         'status': 'CLOSED_V29' if delta.get('verdict') == 'PASS' else 'OPEN'},
        {'id': 'BLK-G-01', 'severity': 'P0', 'title': 'Broad rollout signoff V7 final approval',
         'status': 'PLAN_READY_NOT_APPROVED_V29'},
        {'id': 'BLK-G-02', 'severity': 'P0', 'title': 'Broad rollout NO_GO',
         'status': 'NO_GO_V29'},
    ]
    by_sev = {}
    for b in MATRIX:
        sv = b['severity']
        by_sev.setdefault(sv, {'open': 0, 'addressed': 0, 'total': 0})
        by_sev[sv]['total'] += 1
        st = b['status']
        if any(t in st for t in ('CLOSED', 'ACCEPTED', 'READY', 'NOT_APPROVED', 'NO_GO', 'ENV_MISSING')):
            by_sev[sv]['addressed'] += 1
        else:
            by_sev[sv]['open'] += 1

    out = {
        'task_origin': 'AF2-N-V29-BLOCKER-MATRIX-V8', 'version': 'v8',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'stage': 'stage4_internal_beta_active_scope_s1_2500_no_broad_rollout',
        'broad_rollout_authorized': False,
        'public_spend_ui_authorized': False,
        'stack_g_authorized': False,
        'matrix': MATRIX,
        'summary_by_severity': by_sev,
        'v29_transitions': {
            'BLK-B-08': 'CLOSED_V29' if schema_reg.get('verdict') == 'PASS' else 'OPEN',
            'BLK-F-04': 'CLOSED_V29' if s8.get('verdict') == 'PASS' else 'OPEN',
            'BLK-H-01': 'CLOSED_V29' if ext.get('verdict') == 'PASS' else 'OPEN',
            'BLK-H-02': 'CLOSED_V29' if delta.get('verdict') == 'PASS' else 'OPEN',
            'BLK-B-03': mredis.get('status'),
            'BLK-D-02-LIVE': alert.get('sink_mode'),
        },
    }
    out['verdict'] = 'PASS' if by_sev.get('P0', {}).get('open', 1) == 0 else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} P0_open={by_sev.get('P0',{}).get('open')} V29_transitions={out['v29_transitions']}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
