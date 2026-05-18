#!/usr/bin/env python3
"""V22 — Audit Redis rate-limit migration plan + adapter skeleton."""
from __future__ import annotations
import json, sys
from pathlib import Path

PLAN = Path('/app/data/design/affinity/affinity_rate_limit_redis_migration_plan_v1.json')
ADAPTER = Path('/app/backend/data/affinity_rate_limit_store.py')


def main():
    fails = []
    if not PLAN.exists():
        fails.append('plan_missing'); print('FAIL: plan_missing'); return 2
    d = json.loads(PLAN.read_text())
    if d.get('plan_id') != 'affinity_rate_limit_redis_migration_plan_v1':
        fails.append('plan_id_mismatch')
    if d.get('design_only') is not True:
        fails.append('plan_not_design_only')
    if d.get('live_switch_allowed_this_task') is not False:
        fails.append('live_switch_allowed_true_in_plan')
    for k in ('current_state','target_state','key_design','limits','fallback_behavior','rollout_strategy','rollback_plan','metrics_plan'):
        if k not in d: fails.append(f'missing_section:{k}')
    kd = d.get('key_design', {})
    keys = kd.get('keys', {})
    for k in ('per_user_burst_zset','per_user_minute_zset','per_ip_minute_zset'):
        if k not in keys: fails.append(f'missing_key_pattern:{k}')
    if not ADAPTER.exists():
        fails.append('adapter_missing')
    else:
        t = ADAPTER.read_text()
        for tok in ['AFFINITY_RATE_LIMIT_BACKEND','REDIS_URL','rate_limit_check','redis_available','backend_info','memory','redis']:
            if tok not in t: fails.append(f'adapter_missing_token:{tok}')
    if d.get('broad_rollout_prerequisite') is not True:
        fails.append('not_marked_broad_rollout_prereq')
    if fails:
        for f in fails: print(f'FAIL: {f}')
        return 2
    print('PASS: AF2-N-V22-REDIS-MIGRATION-PLAN-AUDIT')
    return 0


if __name__ == '__main__':
    sys.exit(main())
