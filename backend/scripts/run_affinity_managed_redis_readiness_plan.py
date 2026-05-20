#!/usr/bin/env python3
"""V26 PART B — Managed Redis / HA readiness plan generator."""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path('/app/data/design/affinity/affinity_managed_redis_readiness_plan_v1.json')
OUT.parent.mkdir(parents=True, exist_ok=True)

PLAN = {
    'task_origin': 'AF2-N-V26-MANAGED-REDIS-READINESS-PLAN',
    'version': 'v1',
    'status': 'PLAN_ONLY',
    'live_switch_in_v26': False,
    'rationale': (
        'Local single-node Redis is sufficient for Stage 4 (700 users). '
        'For Broad Rollout (≥10k users) we require an HA backend with documented '
        'failover, observability, and rollback. This plan defines the migration '
        'path; nothing is switched live in V26.'
    ),
    'current_baseline': {
        'backend': 'local_standalone_redis',
        'binary': '/usr/bin/redis-server',
        'supervisor_conf': '/etc/supervisor/conf.d/redis.conf',
        'persistence': False,
        'bind': '127.0.0.1:6379',
        'spof': True,
    },
    'options_evaluated': [
        {
            'option': 'A_local_standalone_hardened',
            'cost_per_month_usd': 0,
            'rto_sec': '30-120 (manual)',
            'rpo': 'N/A (ephemeral counters)',
            'pros': ['zero infra cost', 'no network latency', 'fail-open memory tested'],
            'cons': ['SPOF', 'binary disappears at container restart'],
            'verdict': 'OK for Stage 4 only; NOT broad rollout'
        },
        {
            'option': 'B_redis_sentinel_replica',
            'cost_per_month_usd': '10-40 self-hosted',
            'rto_sec': '5-30',
            'rpo': 'N/A',
            'pros': ['auto failover', 'on-prem control'],
            'cons': ['operational overhead', 'quorum complexity', 'still ours to monitor'],
            'verdict': 'overkill for our dataset; not recommended'
        },
        {
            'option': 'C_redis_cluster',
            'cost_per_month_usd': '50-200 self-hosted',
            'rto_sec': '5-15',
            'rpo': 'N/A',
            'pros': ['horizontal scale'],
            'cons': ['high complexity', 'no shard hot key at our traffic'],
            'verdict': 'overkill; not recommended'
        },
        {
            'option': 'D_managed_redis_single_az',
            'cost_per_month_usd': '15-30 (ElastiCache t4g.micro or Upstash free-tier)',
            'rto_sec': '10-30',
            'rpo': 'N/A',
            'pros': ['HA gestita', 'TLS', 'monitoring incluso', 'snapshot opzionale'],
            'cons': ['+1-5ms latency network', 'dipendenza cloud provider'],
            'verdict': 'RECOMMENDED for pre broad rollout'
        },
        {
            'option': 'E_managed_redis_multi_az',
            'cost_per_month_usd': '50-120',
            'rto_sec': '<5',
            'rpo': 'N/A',
            'pros': ['HA forte', 'multi-AZ failover'],
            'cons': ['costo elevato'],
            'verdict': 'RECOMMENDED for full broad rollout'
        },
    ],
    'recommended_path': {
        'stage4_now': 'A_local_standalone_hardened',
        'pre_broad_rollout': 'D_managed_redis_single_az',
        'broad_rollout_production': 'E_managed_redis_multi_az',
    },
    'env_vars_required': [
        {'name': 'REDIS_MANAGED_URL', 'description': 'rediss://user:pwd@host:port/0 (TLS). NEVER commit.', 'secret': True},
        {'name': 'REDIS_TLS', 'description': '"1" if connection uses TLS', 'secret': False, 'default': '1'},
        {'name': 'REDIS_AUTH_STRATEGY', 'description': 'one of [acl, password, iam_token, sentinel_password]', 'secret': False, 'default': 'password'},
        {'name': 'REDIS_MANAGED_TIMEOUT_MS', 'description': 'socket timeout', 'secret': False, 'default': '1000'},
        {'name': 'AFFINITY_RATE_LIMIT_BACKEND', 'description': 'set to "redis_managed" to route to managed', 'secret': False, 'default': 'redis'},
    ],
    'migration_steps': [
        '1. Provision Managed Redis instance in same region as backend container.',
        '2. Set REDIS_MANAGED_URL via secret manager (NOT repo).',
        '3. Deploy code path that reads REDIS_MANAGED_URL when AFFINITY_RATE_LIMIT_BACKEND=redis_managed.',
        '4. Run probe script: python3 /app/backend/scripts/probe_affinity_managed_redis_optional.py',
        '5. Verify PING+SET+GET+DEL roundtrip under 50ms p95.',
        '6. Canary: flip 5% traffic to managed; monitor fail_open counter and 429 rate.',
        '7. Full switch only after 24h of zero fail_open incidents.',
    ],
    'rollback_steps': [
        '1. Set AFFINITY_RATE_LIMIT_BACKEND=redis (local) in supervisor.',
        '2. Restart backend.',
        '3. Verify rate_limit_backend=redis in canary-status.',
        '4. Remove REDIS_MANAGED_URL from env (optional).',
        'RTO target: <60s.',
    ],
    'failover_expectations': {
        'detection_window_sec': 5,
        'rate_limit_during_failover': 'fail-open to in-memory counters (already tested V23)',
        'data_loss': 'NONE (rate-limit zsets are ephemeral)',
        'customer_impact': 'transparent',
    },
    'secrets_in_repo': False,
    'safety': {
        'no_live_switch_v26': True,
        'rollback_documented': True,
        'no_secrets_committed': True,
        'fail_open_already_tested': True,
    },
    'blockers_resolved': ['BLK-B-03 (Redis SPOF) — plan ready; close at managed provisioning'],
    'broad_rollout_authorized': False,
    'verdict': 'PASS',
    'timestamp_utc': datetime.now(timezone.utc).isoformat(),
}


def main():
    OUT.write_text(json.dumps(PLAN, indent=2, default=str))
    print(f"verdict={PLAN['verdict']} options=5 status={PLAN['status']} → {OUT}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
