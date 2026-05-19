#!/usr/bin/env python3
"""V24 — Validate support/economy prep light."""
from __future__ import annotations
import json, sys
from pathlib import Path

P = Path('/app/data/design/affinity/af2n_v24_support_economy_prep_light_v1.json')
REQ_RUNBOOKS = ['runbook_5xx_surge','runbook_unauthorized_success','runbook_negative_inventory','runbook_borea_leak','runbook_redis_outage']
REQ_SCENARIOS = ['baseline_internal_beta','abuse_one_user','abuse_many_users','10x_cap_stress']


def main():
    if not P.exists(): print(f'FAIL: missing {P}'); return 2
    d = json.loads(P.read_text())
    fails = []
    if d.get('design_only') is not True: fails.append('not_design_only')
    rb_ids = {s.get('id') for s in d.get('support_runbook',{}).get('sections',[])}
    missing = set(REQ_RUNBOOKS) - rb_ids
    if missing: fails.append(f'missing_runbooks:{sorted(missing)}')
    scen_ids = {s.get('scenario') for s in d.get('economy_stress_prep',{}).get('target_scenarios',[])}
    miss_scen = set(REQ_SCENARIOS) - scen_ids
    if miss_scen: fails.append(f'missing_scenarios:{sorted(miss_scen)}')
    if fails:
        for f in fails: print(f'FAIL: {f}')
        return 2
    print('PASS: AF2-N-V24-SUPPORT-ECONOMY-PREP'); return 0


if __name__ == '__main__':
    sys.exit(main())
