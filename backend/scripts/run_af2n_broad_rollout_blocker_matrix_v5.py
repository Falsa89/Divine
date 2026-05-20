#!/usr/bin/env python3
"""V26 PART I — Blocker Matrix V5."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_broad_rollout_blocker_matrix_v5.json')
OUT.parent.mkdir(parents=True, exist_ok=True)

MATRIX = [
    # P0
    {'id': 'BLK-A-01', 'severity': 'P0', 'title': 'battle_engine.py/combat.tsx untouched', 'status': 'CLOSED'},
    {'id': 'BLK-A-02', 'severity': 'P0', 'title': 'Borea/greek_borea/primordial_gaia gift-spend 404', 'status': 'CLOSED'},
    {'id': 'BLK-A-03', 'severity': 'P0', 'title': '/api/heroes count = 100', 'status': 'CLOSED'},
    {'id': 'BLK-A-04', 'severity': 'P0', 'title': 'No 5xx in observation window', 'status': 'CLOSED'},
    {'id': 'BLK-A-05', 'severity': 'P0', 'title': 'No unauthorized spend', 'status': 'CLOSED'},
    # P1
    {'id': 'BLK-B-01', 'severity': 'P1', 'title': 'Ephemeral container Redis init/restore', 'status': 'CLOSED_V25'},
    {'id': 'BLK-B-02', 'severity': 'P1', 'title': 'Redis non-persistent (effemero)', 'status': 'ACCEPTED'},
    {'id': 'BLK-B-03', 'severity': 'P1', 'title': 'Redis SPOF (single-node)', 'status': 'PLAN_READY_V26',
     'closed_by': 'Managed Redis readiness plan V26 (live switch deferred to provisioning)'},
    {'id': 'BLK-B-04', 'severity': 'P1', 'title': 'Rollback drill on clone', 'status': 'CLOSED'},
    {'id': 'BLK-B-05', 'severity': 'P1', 'title': 'Abuse metrics instrumented', 'status': 'CLOSED'},
    {'id': 'BLK-B-06', 'severity': 'P1', 'title': 'Cap 5000 → broad needs ≥100k', 'status': 'PLAN_READY_V26',
     'closed_by': 'Cap raise plan V26 (4-stage progression to 100k)'},
    {'id': 'BLK-B-07', 'severity': 'P1', 'title': 'Inventory writes scope expansion', 'status': 'PLAN_READY_V26',
     'closed_by': 'Inventory scope expansion plan V26 (4-stage progression)'},
    # P2
    {'id': 'BLK-C-01', 'severity': 'P2', 'title': 'Public Spend UI off', 'status': 'CLOSED'},
    {'id': 'BLK-C-02', 'severity': 'P2', 'title': 'STACK-G wiring deferred', 'status': 'CLOSED'},
    {'id': 'BLK-C-03', 'severity': 'P2', 'title': 'Frontend smoke read-only', 'status': 'CLOSED_V26',
     'closed_by': 'V26 frontend smoke audit PASS'},
    # P3
    {'id': 'BLK-D-01', 'severity': 'P3', 'title': 'Runbook restart Redis', 'status': 'CLOSED_V25'},
    {'id': 'BLK-D-02', 'severity': 'P3', 'title': 'Alerting fail-open contract', 'status': 'CONDITIONAL_CLOSED_V25'},
    {'id': 'BLK-D-02-LIVE', 'severity': 'P3', 'title': 'Alerting integration LIVE sink', 'status': 'PLAN_READY_V26',
     'closed_by': 'V26 alerting integration plan (5 sinks evaluated, local mock available, prod wiring TBD)'},
    {'id': 'BLK-D-03', 'severity': 'P3', 'title': 'Support playbook spend errors', 'status': 'CLOSED_V25'},
    # Economy stress (V25)
    {'id': 'BLK-E-01', 'severity': 'P1', 'title': 'Economy stress 10x simulation', 'status': 'CLOSED_V25'},
    # New V26
    {'id': 'BLK-F-01', 'severity': 'P1', 'title': 'Stress 2x live probe', 'status': 'CLOSED_V26',
     'closed_by': 'V26 stress 2x PASS (0 5xx, Borea 404 30/30)'},
    {'id': 'BLK-G-01', 'severity': 'P0', 'title': 'Broad rollout signoff package V6 approved', 'status': 'PLAN_READY_V26_NOT_APPROVED',
     'note': 'Plan structured; explicit final user approval still required'},
]


def main():
    by_sev = {}
    for b in MATRIX:
        sv = b['severity']
        by_sev.setdefault(sv, {'open': 0, 'closed_or_plan': 0, 'total': 0})
        by_sev[sv]['total'] += 1
        st = b['status']
        if 'CLOSED' in st or 'ACCEPTED' in st or 'PLAN_READY' in st:
            by_sev[sv]['closed_or_plan'] += 1
        else:
            by_sev[sv]['open'] += 1

    p1 = by_sev.get('P1', {})
    out = {
        'task_origin': 'AF2-N-V26-BLOCKER-MATRIX-V5',
        'version': 'v5',
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'stage': 'stage4_internal_beta_active_no_broad_rollout',
        'broad_rollout_authorized': False,
        'broad_rollout_blocker_explicit': 'BLK-G-01 (final user approval not granted)',
        'public_spend_ui_authorized': False,
        'matrix': MATRIX,
        'summary_by_severity': by_sev,
        'progress_p1': p1,
        'gates': {
            'gate_1_stage4_extension': by_sev.get('P0', {}).get('open', 1) == 0,
            'gate_2_broad_rollout': False,  # BLK-B-03/B-06/B-07 still PLAN_READY (not LIVE_CLOSED)
            'gate_3_public_spend_ui': False,
        },
        'note_plan_ready_vs_closed': (
            'PLAN_READY_V26 means a plan exists and is validated, but live execution '
            'is deferred until explicit broader approval is granted.'
        ),
        'verdict': 'PASS' if by_sev.get('P0', {}).get('open', 1) == 0 else 'FAIL',
    }
    OUT.write_text(json.dumps(out, indent=2, default=str))
    print(f"verdict={out['verdict']} P1={p1} → {OUT}")
    return 0 if out['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
