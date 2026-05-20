#!/usr/bin/env python3
"""V26 PART E — Broad-rollout signoff package V6 (PLAN-ONLY, BLOCKED)."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_broad_rollout_signoff_package_v6.json')
OUT.parent.mkdir(parents=True, exist_ok=True)

DOMAINS = [
    {
        'domain': 'product',
        'owner_role': 'Product Manager',
        'status': 'PENDING',
        'evidence_required': [
            'PRD finale broad rollout',
            'KPI di successo (DAU/MAU, conversion)',
            'comms plan ai giocatori esistenti',
        ],
        'gate_passed': False,
    },
    {
        'domain': 'engineering',
        'owner_role': 'Backend Lead',
        'status': 'PENDING',
        'evidence_required': [
            'Managed Redis multi-AZ live',
            'cap raise S3 ≥100k',
            'inventory scope S3 expansion',
            'idempotency index unique+sparse verified in CI',
            'all V21→V25 validators PASS in CI/CD pipeline',
        ],
        'gate_passed': False,
    },
    {
        'domain': 'qa',
        'owner_role': 'QA Lead',
        'status': 'PENDING',
        'evidence_required': [
            'Stress 2x PASS (V26)',
            'Stress 5x PASS (future)',
            'Stress 10x PASS (future)',
            'frontend smoke PASS',
            'a11y audit PASS',
            'cross-platform iOS+Android smoke',
        ],
        'gate_passed': False,
    },
    {
        'domain': 'economy',
        'owner_role': 'Economy Ops',
        'status': 'PENDING',
        'evidence_required': [
            'Stress 10x simulation reviewed',
            'inventory replenishment mechanic decided',
            'refund policy documented',
            'cap raise plan approved per stage',
        ],
        'gate_passed': False,
    },
    {
        'domain': 'rollback',
        'owner_role': 'Backend Lead',
        'status': 'PARTIAL',
        'evidence_required': [
            'V24 clone rollback drill PASS',
            'V25 Redis restart drill PASS',
            'V25 rollback readiness PASS',
            'Production DB backup automation verified',
            'V26 rollback readiness PASS',
        ],
        'gate_passed': False,
        'progress_pct': 60,
    },
    {
        'domain': 'security_abuse',
        'owner_role': 'Security',
        'status': 'PARTIAL',
        'evidence_required': [
            'Borea/hidden alias 404 (V24 PASS, V25 PASS, V26 PASS)',
            'rate-limit Redis backed (V23 PASS)',
            'abuse metrics instrumented (V24 PASS)',
            'fail-open alerting contract (V25 PASS)',
            'alerting integration LIVE (still pending)',
            'pentest report for spend endpoint',
        ],
        'gate_passed': False,
        'progress_pct': 70,
    },
    {
        'domain': 'support_ops',
        'owner_role': 'Support Lead',
        'status': 'PARTIAL',
        'evidence_required': [
            'Support runbook V25 PASS',
            '24/7 staffing plan for broad rollout',
            'customer comms templates approved',
            'escalation paging tested',
        ],
        'gate_passed': False,
        'progress_pct': 50,
    },
    {
        'domain': 'final_user_approval',
        'owner_role': 'Project Owner (user)',
        'status': 'NOT_YET_REQUESTED',
        'evidence_required': [
            'All above domains PASSED',
            'Final review of V26+ readiness',
            'Explicit GO from project owner',
        ],
        'gate_passed': False,
    },
]


def main():
    package = {
        'task_origin': 'AF2-N-V26-BROAD-ROLLOUT-SIGNOFF-PACKAGE-V6',
        'version': 'v6',
        'status': 'PLAN_ONLY',
        'gates_passed': 0,
        'gates_total': len(DOMAINS),
        'broad_rollout_allowed': False,
        'public_spend_ui_allowed': False,
        'STACK_G_allowed': False,
        'domains': DOMAINS,
        'required_evidence_count': sum(len(d['evidence_required']) for d in DOMAINS),
        'blockers_from_matrix_v5': [
            'BLK-B-03 Redis SPOF (Managed Redis pre-broad)',
            'BLK-B-06 cap raise plan in progress',
            'BLK-B-07 inventory scope expansion in progress',
            'BLK-C-03 frontend gift-spend UI smoke (gated)',
            'BLK-D-02-LIVE alerting integration live sink pending',
        ],
        'final_user_approval_required': True,
        'final_user_approval_granted': False,
        'safety_invariants': [
            'Borea hidden/404',
            '/api/heroes=100',
            'no battle wiring',
            'no public spend UI',
            'no STACK-G',
            'no broad rollout',
        ],
        'verdict': 'PASS',  # PASS = package correctly structured as plan-only-blocked
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
    }
    OUT.write_text(json.dumps(package, indent=2, default=str))
    print(f"verdict={package['verdict']} gates={package['gates_passed']}/{package['gates_total']} broad_allowed=False → {OUT}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
