#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(R, 'data/design/v110_pack_95_reward_ledger_story_write_legacy_guards/v110_pack_95_baseline_multirun_v1.json')
d = json.load(open(p))
runs = d.get('runs') or []
assert len(runs) >= 3, f'expected 3 runs, got {len(runs)}'
sig0 = (runs[0]['pass'], runs[0]['fail'], runs[0]['miss'])
for r in runs[1:]:
    assert (r['pass'], r['fail'], r['miss']) == sig0, f'baseline NOT deterministic: {r} vs {sig0}'
assert d.get('deterministic') is True
print(f'[v110 PACK_95_BASELINE_MULTIRUN] OK deterministic baseline_signature={d.get("baseline_signature")}')
