#!/usr/bin/env python3
"""V26 PART D — Inventory scope expansion plan (PLAN ONLY)."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_inventory_scope_expansion_plan_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)

STAGES = [
    {'stage': 'S0_current', 'users_with_inventory_writes': '~150 (Stage1 subset)',
     'description': 'AFFINITY_GIFT_INVENTORY_WRITES_ENABLED true for Stage1 allowlist subset.',
     'risk_level': 'LOW'},
    {'stage': 'S1_full_stage4', 'users_with_inventory_writes': 700,
     'description': 'Expand to all Stage 4 allowlist (700 QA users).',
     'prereq': ['cap raise plan S1 approved', 'support runbook V25', 'all V25 P0 closed'],
     'risk_level': 'LOW',
     'seed_strategy': 'opt-in per user; never blanket; idempotent INSERT-IF-MISSING',
     'reconciliation': 'V22 inventory delta audit must PASS daily',
     'rollback': 'unset AFFINITY_GIFT_INVENTORY_WRITES_ENABLED + restart'},
    {'stage': 'S2_internal_beta_2k', 'users_with_inventory_writes': 2500,
     'description': 'Internal Beta expansion. Allowlist still required.',
     'prereq': ['Managed Redis ready', 'cap S1 → S2', 'alerting integration live', 'observation 72h post-S1'],
     'risk_level': 'MEDIUM',
     'seed_strategy': 'opt-in + cohort batch (≤500 users/day)',
     'rollback': 'freeze writes flag; ledger remains read-only'},
    {'stage': 'S3_internal_beta_full', 'users_with_inventory_writes': 7000,
     'prereq': ['Multi-AZ Redis', 'broad rollout signoff V6 approved', 'support staffing 24/7'],
     'risk_level': 'MEDIUM-HIGH',
     'seed_strategy': 'opt-in only; daily reconciliation',
     'rollback': 'unset flag + clone rollback drill ready'},
    {'stage': 'S4_broad_rollout', 'users_with_inventory_writes': 'all eligible',
     'prereq': ['ALL of S3 + STACK-G decision separate'],
     'risk_level': 'HIGH',
     'gate': 'Explicit final user approval per signoff V6'},
]

CONSTRAINTS = {
    'anti_negative_inventory': {
        'rule': 'inventory updates use $inc with explicit lower-bound check',
        'enforcement': 'application + index integrity; never go below 0',
        'alert': 'V25 alert rule negative_inventory P0',
    },
    'reconciliation_strategy': {
        'frequency': 'daily',
        'script': '/app/backend/scripts/validate_affinity_inventory_delta_consistency_v23.py',
        'tolerance': 'zero mismatches',
    },
    'borea_hidden_invariant': {
        'enforcement': 'gift-spend route rejects Borea/greek_borea/primordial_gaia BEFORE any inventory mutation',
        'verified_in': ['V21 audit', 'V22 audit', 'V23 audit', 'V24 audit', 'V25 audit', 'V26 preflight'],
        'must_remain': True,
    },
    'support_ops': {
        'runbook': '/app/docs/divine/85_AF2N_STAGE4_SUPPORT_RUNBOOK_V25.md',
        'escalation_matrix': 'V25 §9',
        'inventory_issue_section': 'V25 §4',
    },
}

PLAN = {
    'task_origin': 'AF2-N-V26-INVENTORY-SCOPE-EXPANSION-PLAN',
    'version': 'v1',
    'status': 'PLAN_ONLY',
    'live_expansion_in_v26': False,
    'current_scope': 'Stage1 subset (~150 users)',
    'target_scope': 'broad rollout all eligible',
    'stages': STAGES,
    'constraints': CONSTRAINTS,
    'rollback_steps': [
        '1. unset AFFINITY_GIFT_INVENTORY_WRITES_ENABLED in backend.conf',
        '2. restart backend',
        '3. verify canary-status inventory_mutation_enabled=false',
        '4. ledger remains intact, reads still allowed',
        'RTO target: <90s',
    ],
    'safety': {
        'no_live_expansion_v26': True,
        'borea_hidden_preserved': True,
        'anti_negative_inventory_enforced': True,
        'rollback_per_stage_documented': True,
        'no_unauthorized_spend': True,
    },
    'broad_rollout_authorized': False,
    'verdict': 'PASS',
    'timestamp_utc': datetime.now(timezone.utc).isoformat(),
}


def main():
    OUT.write_text(json.dumps(PLAN, indent=2, default=str))
    print(f"verdict={PLAN['verdict']} stages={len(STAGES)} → {OUT}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
