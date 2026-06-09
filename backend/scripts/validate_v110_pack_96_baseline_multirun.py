#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_96_reward_claim_ledger_live_execute/v110_pack_96_baseline_multirun_v1.json')))
runs = d.get('runs') or []
assert len(runs) >= 3
sig0 = (runs[0]['pass'], runs[0]['fail'], runs[0]['miss'])
for r in runs[1:]:
    assert (r['pass'], r['fail'], r['miss']) == sig0, f'baseline NOT deterministic'
assert d.get('deterministic') is True
print(f'[v110 PACK_96_BASELINE_MULTIRUN] OK deterministic baseline={d.get("baseline_signature")}')
