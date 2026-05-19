#!/usr/bin/env python3
"""V24 — Validate Redis HA decision plan."""
from __future__ import annotations
import json, sys
from pathlib import Path

P = Path('/app/data/design/affinity/affinity_rate_limit_redis_ha_decision_plan_v1.json')
REQ_SECTIONS = ['current_state','options_considered','recommended_target','migration_phases','rollback_plan','slo_targets','hard_invariants']
REQ_OPTIONS = ['single_node_no_ha','redis_sentinel','redis_cluster','managed_redis_service']


def main():
    if not P.exists(): print(f'FAIL: missing {P}'); return 2
    d = json.loads(P.read_text())
    fails = []
    if d.get('design_only') is not True: fails.append('not_design_only')
    if d.get('live_switch_allowed_this_task') is not False: fails.append('live_switch_allowed_true')
    for s in REQ_SECTIONS:
        if s not in d: fails.append(f'missing_section:{s}')
    opts = {o.get('option') for o in d.get('options_considered', [])}
    missing_opts = set(REQ_OPTIONS) - opts
    if missing_opts: fails.append(f'missing_options:{sorted(missing_opts)}')
    rec = d.get('recommended_target', {})
    if rec.get('primary') not in ('redis_sentinel','redis_cluster','managed_redis_service'):
        fails.append('bad_recommended_primary')
    phases = d.get('migration_phases', {})
    if 'phase_7_BROAD_ROLLOUT_PREREQ' not in phases:
        fails.append('missing_broad_rollout_prereq_phase')
    if fails:
        for f in fails: print(f'FAIL: {f}')
        return 2
    print('PASS: AF2-N-V24-REDIS-HA-DECISION-PLAN'); return 0


if __name__ == '__main__':
    sys.exit(main())
