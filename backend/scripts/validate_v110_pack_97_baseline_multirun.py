#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_97_daily_login_claim_frontend_unlock/v110_pack_97_baseline_multirun_v1.json')))
runs = d['runs']
assert len(runs) >= 3
sig0 = (runs[0]['pass'], runs[0]['fail'], runs[0]['miss'])
for r in runs[1:]:
    assert (r['pass'], r['fail'], r['miss']) == sig0, 'NOT deterministic'
assert d['deterministic'] is True
print(f'[v110 PACK_97_BASELINE_MULTIRUN] OK baseline={d["baseline_signature"]}')
