#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_91_inventory_frontend_consumer_and_smoke/v110_pack_91_baseline_multirun_v1.json')))
for k in ('baseline_pre_pack_run1','baseline_pre_pack_run2','baseline_pre_pack_run3'):
    r = d.get(k); assert r and r.get('required_fail') == 0 and r.get('miss') == 0
p1 = d['baseline_pre_pack_run1']['pass']; p2 = d['baseline_pre_pack_run2']['pass']; p3 = d['baseline_pre_pack_run3']['pass']
assert p1 == p2 == p3 and d.get('deterministic') is True
print(f'[v110 PACK_91_BASELINE_MULTIRUN] OK run1=run2=run3={p1} required=0 miss=0')
