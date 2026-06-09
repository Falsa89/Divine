#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(R, 'data/design/v110_pack_96_reward_claim_ledger_live_execute/v110_pack_96_final_multirun_suite_result_v1.json')
assert os.path.exists(p), 'final multirun result missing'
d = json.load(open(p))
runs = d.get('runs') or []
assert len(runs) >= 3
sig0 = (runs[0]['pass'], runs[0]['fail'], runs[0]['miss'])
for r in runs[1:]:
    assert (r['pass'], r['fail'], r['miss']) == sig0, 'final NOT deterministic'
assert d.get('deterministic') is True
assert d.get('miss_zero_all_runs') is True
print(f'[v110 PACK_96_FINAL_MULTIRUN_SUITE] OK deterministic final_signature={d.get("final_signature")} miss=0')
