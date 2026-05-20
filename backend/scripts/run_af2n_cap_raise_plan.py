#!/usr/bin/env python3
"""V26 PART C — Cap raise plan 5k → ≥100k (PLAN ONLY)."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/af2n_cap_raise_plan_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)

STAGES = [
    {'stage': 'S0_current', 'cap': 5000, 'users_target': 700, 'rationale': 'Stage 4 Internal Beta active'},
    {'stage': 'S1', 'cap': 25000, 'users_target': 2500, 'redis_ops_per_sec_p95': 30,
     'gate': 'Local Redis OK; bump cap when 70% of S0 cap reached.',
     'rollback_threshold': 'fail_open > 50/h OR 5xx > 0 OR delta_mismatch > 0'},
    {'stage': 'S2', 'cap': 50000, 'users_target': 7000, 'redis_ops_per_sec_p95': 60,
     'gate': 'Managed Redis single-AZ provisioned (Plan B option D).',
     'rollback_threshold': 'fail_open > 100/h OR 5xx > 0 OR p95_latency > 200ms'},
    {'stage': 'S3', 'cap': 100000, 'users_target': 15000, 'redis_ops_per_sec_p95': 120,
     'gate': 'Managed Redis multi-AZ; alerting integration live; broad rollout signoff V6 approved.',
     'rollback_threshold': 'any P0 alert firing'},
    {'stage': 'S4_open', 'cap': 'unlimited+per-user-quota', 'users_target': 'all', 'redis_ops_per_sec_p95': 500,
     'gate': 'Full broad rollout authorized; STACK-G wiring decision separate.',
     'rollback_threshold': 'P0 alert OR economy ops emergency'},
]

PRESSURE = {
    'ledger_growth_per_step': 'avg 5 rows/user spread over 30 days = ~3% per day',
    'redis_keys_at_S3': {
        'zset_per_user': 3,  # user_burst, user_min, user_hour
        'zset_per_ip': 1,    # ip_min
        'estimated_max': 15000 * 3 + 5000,  # users*3 zsets + ip zsets cap
    },
    'mongo_indexes_required': [
        'gift_transaction_ledger: {idempotency_key: 1} unique sparse',
        'gift_transaction_ledger: {user_id: 1, created_at_utc: -1}',
        'user_gift_inventory: {user_id: 1} unique',
        'user_affinity_state: {user_id: 1, hero_id: 1} unique',
    ],
    'inventory_seed_required': True,
    'inventory_seed_strategy': 'per-stage opt-in: only seed users moving into stage; never blanket seed.',
}

PLAN = {
    'task_origin': 'AF2-N-V26-CAP-RAISE-PLAN',
    'version': 'v1',
    'status': 'PLAN_ONLY',
    'live_cap_change_in_v26': False,
    'current_cap': 5000,
    'target_cap': 100000,
    'stages': STAGES,
    'pressure_analysis': PRESSURE,
    'rollback_steps': [
        '1. Set AFFINITY_GIFT_CANARY_LEDGER_CAP back to previous stage value in supervisor.',
        '2. Restart backend.',
        '3. Verify canary-status canary_ledger_cap matches expected.',
        '4. Stop allowlist expansion if rolling back.',
        'RTO target: <2 minutes.',
    ],
    'safety': {
        'no_live_cap_change': True,
        'borea_hidden_preserved_across_stages': True,
        'no_unauthorized_spend': True,
        'rollback_documented_per_stage': True,
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
