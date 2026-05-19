#!/usr/bin/env python3
"""V25 PART G — Generate Blocker Matrix V4 JSON."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v4.json')
OUT.parent.mkdir(parents=True, exist_ok=True)

MATRIX = [
    # P0 (absolute)
    {'id': 'BLK-A-01', 'severity': 'P0', 'title': 'battle_engine.py/combat.tsx untouched', 'status': 'CLOSED', 'owner': 'backend'},
    {'id': 'BLK-A-02', 'severity': 'P0', 'title': 'Borea/greek_borea/primordial_gaia gift-spend 404', 'status': 'CLOSED', 'owner': 'backend'},
    {'id': 'BLK-A-03', 'severity': 'P0', 'title': '/api/heroes count = 100', 'status': 'CLOSED', 'owner': 'backend'},
    {'id': 'BLK-A-04', 'severity': 'P0', 'title': 'No 5xx in observation window', 'status': 'CLOSED', 'owner': 'backend'},
    {'id': 'BLK-A-05', 'severity': 'P0', 'title': 'No unauthorized spend', 'status': 'CLOSED', 'owner': 'backend'},
    # P1 (broad rollout)
    {'id': 'BLK-B-01', 'severity': 'P1', 'title': 'Ephemeral container Redis init/restore', 'status': 'CLOSED_V25', 'owner': 'infra',
     'closed_by': '/app/ops/ensure_redis_rate_limit.sh (idempotent)'},
    {'id': 'BLK-B-02', 'severity': 'P1', 'title': 'Redis non-persistent (effemero)', 'status': 'ACCEPTED', 'owner': 'infra',
     'rationale': 'Rate-limit data is by-design ephemeral'},
    {'id': 'BLK-B-03', 'severity': 'P1', 'title': 'Redis SPOF (single-node)', 'status': 'OPEN', 'owner': 'infra',
     'plan': 'Managed Redis pre-broad-rollout (V26 gate)'},
    {'id': 'BLK-B-04', 'severity': 'P1', 'title': 'Rollback drill on clone', 'status': 'CLOSED', 'owner': 'backend',
     'closed_by': 'V24 clone rollback drill PASS'},
    {'id': 'BLK-B-05', 'severity': 'P1', 'title': 'Abuse metrics instrumented', 'status': 'CLOSED', 'owner': 'backend',
     'closed_by': 'V24 metrics-snapshot endpoint live'},
    {'id': 'BLK-B-06', 'severity': 'P1', 'title': 'Cap 5000 → broad rollout needs ≥100k', 'status': 'OPEN', 'owner': 'economy',
     'plan': 'V26 signoff package'},
    {'id': 'BLK-B-07', 'severity': 'P1', 'title': 'Inventory writes scope=Stage1 subset', 'status': 'OPEN', 'owner': 'backend',
     'plan': 'V26 signoff package'},
    # P2 (public ui)
    {'id': 'BLK-C-01', 'severity': 'P2', 'title': 'Public Spend UI off', 'status': 'CLOSED', 'owner': 'frontend'},
    {'id': 'BLK-C-02', 'severity': 'P2', 'title': 'STACK-G wiring deferred', 'status': 'CLOSED', 'owner': 'backend'},
    {'id': 'BLK-C-03', 'severity': 'P2', 'title': 'Frontend gift-spend UI smoke test', 'status': 'OPEN', 'owner': 'frontend',
     'plan': 'Plan-only until Public Spend UI gate'},
    # P3 (nice-to-have)
    {'id': 'BLK-D-01', 'severity': 'P3', 'title': 'Runbook restart Redis', 'status': 'CLOSED_V25', 'owner': 'docs',
     'closed_by': '/app/docs/divine/85_AF2N_STAGE4_SUPPORT_RUNBOOK_V25.md + /app/ops/README_REDIS_RATE_LIMIT_RECOVERY.md'},
    {'id': 'BLK-D-02', 'severity': 'P3', 'title': 'Alerting fail-open', 'status': 'CONDITIONAL_CLOSED_V25', 'owner': 'infra',
     'closed_by': 'af2n_fail_open_alerting_contract_v1.json + readonly status snapshot',
     'conditional': 'Contract defined; live alerting integration TBD (Prometheus/PagerDuty next)'},
    {'id': 'BLK-D-03', 'severity': 'P3', 'title': 'Support playbook for spend errors', 'status': 'CLOSED_V25', 'owner': 'support',
     'closed_by': 'V25 Support Runbook'},
    # Added in V25
    {'id': 'BLK-E-01', 'severity': 'P1', 'title': 'Economy stress 10x simulation', 'status': 'CLOSED_V25', 'owner': 'economy',
     'closed_by': 'af2n_economy_stress_10x_simulation_v25_result.json (PASS, 5 recommendations)'},
]


def main():
    by_sev = {}
    for b in MATRIX:
        by_sev.setdefault(b['severity'], {'open': 0, 'closed': 0, 'total': 0})
        by_sev[b['severity']]['total'] += 1
        st = b['status']
        if 'CLOSED' in st or 'ACCEPTED' in st:
            by_sev[b['severity']]['closed'] += 1
        else:
            by_sev[b['severity']]['open'] += 1

    out = {
        'task_origin': 'AF2-N-V25-BROAD-ROLLOUT-BLOCKER-MATRIX-V4',
        'version': 'v4',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'stage': 'stage4_internal_beta_active_no_broad_rollout',
        'broad_rollout_authorized': False,
        'public_spend_ui_authorized': False,
        'matrix': MATRIX,
        'summary_by_severity': by_sev,
        'p0_all_closed': by_sev.get('P0', {}).get('open', 1) == 0,
        'p1_progress': {
            'closed': by_sev.get('P1', {}).get('closed', 0),
            'total': by_sev.get('P1', {}).get('total', 0),
        },
        'gates': {
            'gate_1_stage4_extension': by_sev.get('P0', {}).get('open', 1) == 0,
            'gate_2_broad_rollout': False,  # at least 2 P1 still open (BLK-B-03, B-06, B-07)
            'gate_3_public_spend_ui': False,  # strictly deferred
        },
        'verdict': 'PASS' if by_sev.get('P0', {}).get('open', 1) == 0 else 'FAIL',
    }
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} P0_closed={out['p0_all_closed']} P1={by_sev.get('P1')} → {OUT}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
