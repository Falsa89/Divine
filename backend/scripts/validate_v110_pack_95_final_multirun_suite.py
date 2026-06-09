#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(R, 'data/design/v110_pack_95_reward_ledger_story_write_legacy_guards/v110_pack_95_final_multirun_suite_result_v1.json')
assert os.path.exists(p), 'final multirun suite result missing'
d = json.load(open(p))
runs = d.get('runs') or []
assert len(runs) >= 3
sig0 = (runs[0]['pass'], runs[0]['fail'], runs[0]['miss'])
for r in runs[1:]:
    assert (r['pass'], r['fail'], r['miss']) == sig0, f'final NOT deterministic'
assert d.get('deterministic') is True
assert d.get('miss_zero_all_runs') is True
print(f'[v110 PACK_95_FINAL_MULTIRUN_SUITE] OK deterministic final_signature={d.get("final_signature")} miss=0')
