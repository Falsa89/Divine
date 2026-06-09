#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_92_core_server_scope/v110_pack_92_baseline_multirun_v1.json')))
for k in ('baseline_pre_pack_run1','baseline_pre_pack_run2','baseline_pre_pack_run3'):
    r = d.get(k); assert r and r.get('required_fail') == 0 and r.get('miss') == 0
p1, p2, p3 = (d['baseline_pre_pack_run' + str(i)]['pass'] for i in (1,2,3))
assert p1 == p2 == p3 and d.get('deterministic') is True
print(f'[v110 PACK_92_BASELINE_MULTIRUN] OK run1=run2=run3={p1} required=0 miss=0')
