#!/usr/bin/env python3
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data/design/v110_pack_98_daily_home_unlock_quest_claim/v110_pack_98_final_multirun_suite_result_v1.json')
assert os.path.exists(p)
d=json.load(open(p))
rs=d.get('runs')or[]; assert len(rs)>=3
sig=(rs[0]['pass'],rs[0]['fail'],rs[0]['miss'])
for r in rs[1:]: assert (r['pass'],r['fail'],r['miss'])==sig
assert d['deterministic'] is True and d['miss_zero_all_runs'] is True
print(f'[v110 PACK_98_FINAL_MULTIRUN_SUITE] OK deterministic final={d["final_signature"]} miss=0')
