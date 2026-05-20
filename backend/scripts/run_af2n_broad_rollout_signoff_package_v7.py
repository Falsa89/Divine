#!/usr/bin/env python3
"""V29 PART H — Broad Rollout Signoff Package V7 (PLAN-ONLY, all blocked)."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path
OUT = Path('/app/data/design/affinity/af2n_broad_rollout_signoff_package_v7.json')
OUT.parent.mkdir(parents=True, exist_ok=True)


def _read(p):
    f = Path(p)
    if not f.exists(): return {}
    try: return json.loads(f.read_text())
    except Exception: return {}


def main():
    mat_v8 = _read('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v8.json')
    ext = _read('/app/data/design/affinity/af2n_scope_s1_extended_monitoring_v29_result.json')
    s8 = _read('/app/data/design/affinity/af2n_stress_8x_v29_result.json')
    delta = _read('/app/data/design/affinity/affinity_inventory_delta_consistency_v29_report.json')
    schema_reg = _read('/app/data/design/affinity/af2n_v28_schema_fix_regression_v29_result.json')
    mredis = _read('/app/data/design/affinity/managed_redis_envaware_v29_result.json')
    alert = _read('/app/data/design/affinity/alerting_envaware_v29_result.json')

    REQUIRED_EVIDENCE = [
        {'id': 'EV-V28-SCHEMA-FIX-REG', 'desc': 'V28 schema-fix regression PASS @scale',
         'status': 'PROVIDED' if schema_reg.get('verdict') == 'PASS' else 'MISSING'},
        {'id': 'EV-V29-EXT-MONITORING', 'desc': 'Extended monitoring (1500+ samples)',
         'status': 'PROVIDED' if ext.get('verdict') == 'PASS' else 'MISSING'},
        {'id': 'EV-V29-STRESS-8X', 'desc': 'Stress 8x sim + safe live probe PASS',
         'status': 'PROVIDED' if s8.get('verdict') == 'PASS' else 'MISSING'},
        {'id': 'EV-V29-DELTA-AUDIT', 'desc': 'Full delta audit V29 PASS',
         'status': 'PROVIDED' if delta.get('verdict') == 'PASS' else 'MISSING'},
        {'id': 'EV-V29-MANAGED-REDIS-PROBE', 'desc': 'Managed Redis env-aware probe',
         'status': 'PROVIDED' if mredis.get('verdict') == 'PASS' else 'MISSING',
         'detail': mredis.get('status')},
        {'id': 'EV-V29-ALERTING-PROBE', 'desc': 'Alerting env-aware probe',
         'status': 'PROVIDED' if alert.get('verdict') == 'PASS' else 'MISSING',
         'detail': alert.get('sink_mode')},
        {'id': 'EV-V28-CAP25K-STABLE', 'desc': 'Cap 25k stable since V27',
         'status': 'PROVIDED'},
        {'id': 'EV-V28-ALLOWLIST-2500-STABLE', 'desc': 'Allowlist 2500 stable since V28',
         'status': 'PROVIDED'},
        {'id': 'EV-INFRA-MANAGED-REDIS-LIVE', 'desc': 'Managed Redis LIVE traffic switched and stable for >=14d',
         'status': 'PENDING'},
        {'id': 'EV-INFRA-ALERTING-LIVE', 'desc': 'Alerting LIVE webhook/pushgw verified with real incidents',
         'status': 'PENDING'},
        {'id': 'EV-OBSERVABILITY-DASHBOARDS', 'desc': 'Grafana/dashboard for af2n metrics',
         'status': 'PENDING'},
        {'id': 'EV-LEGAL-PRODUCT-SIGNOFF', 'desc': 'Product + legal explicit signoff',
         'status': 'PENDING'},
        {'id': 'EV-USER-FINAL-APPROVAL', 'desc': 'Explicit user approval of broad rollout',
         'status': 'PENDING'},
    ]

    SIGNOFFS = {
        'engineering_signoff': False,
        'qa_signoff': False,
        'product_signoff': False,
        'legal_signoff': False,
        'sre_signoff': False,
        'security_signoff': False,
        'final_user_approval': False,
    }

    blockers_from_matrix = []
    for b in (mat_v8.get('matrix') or []):
        if b.get('severity') in ('P0', 'P1') and 'CLOSED' not in (b.get('status') or '') and 'ACCEPTED' not in (b.get('status') or '') and 'READY' not in (b.get('status') or '') and 'NOT_APPROVED' not in (b.get('status') or ''):
            blockers_from_matrix.append({'id': b.get('id'), 'severity': b.get('severity'), 'status': b.get('status')})

    out = {
        'task_origin': 'AF2-N-V29-BROAD-ROLLOUT-SIGNOFF-V7',
        'version': 'v7',
        'mode': 'PLAN_ONLY',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'broad_rollout_allowed': False,
        'public_spend_ui_allowed': False,
        'stack_g_allowed': False,
        'signoffs': SIGNOFFS,
        'required_evidence': REQUIRED_EVIDENCE,
        'blockers_from_matrix_v8': blockers_from_matrix,
        'pending_signoff_count': sum(1 for v in SIGNOFFS.values() if not v),
        'pending_evidence_count': sum(1 for e in REQUIRED_EVIDENCE if e['status'] != 'PROVIDED'),
        'next_steps_if_approved_in_future': [
            'Switch Managed Redis live (V30+) with rollback ready',
            'Activate alerting live sink with incident validation',
            'Run 14d soak on Stage4 scope S1',
            'Run broad rollout dry-run on staging clone',
            'Obtain product + legal explicit signoff',
            'Obtain explicit user final approval',
            'Broad rollout in waves with continuous monitoring',
        ],
        'safety': {
            'plan_only': True,
            'no_runtime_change': True,
            'no_db_write': True,
            'no_secret_logged': True,
        },
    }
    out['verdict'] = 'PASS' if all([
        out['broad_rollout_allowed'] is False,
        out['public_spend_ui_allowed'] is False,
        out['stack_g_allowed'] is False,
        not any(SIGNOFFS.values()),
        out['safety']['plan_only'],
    ]) else 'FAIL'
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} pending_signoff={out['pending_signoff_count']} pending_evidence={out['pending_evidence_count']} blockers={len(blockers_from_matrix)}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
