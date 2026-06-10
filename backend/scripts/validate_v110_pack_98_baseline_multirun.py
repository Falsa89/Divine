#!/usr/bin/env python3
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_baseline_multirun_v1.json')))
assert d['deterministic'] is True
rs=d['runs']; assert len(rs)>=3
sig=(rs[0]['pass'],rs[0]['fail'],rs[0]['miss'])
for r in rs[1:]: assert (r['pass'],r['fail'],r['miss'])==sig
print(f'[v110 PACK_98_BASELINE_MULTIRUN] OK baseline={d["baseline_signature"]}')
