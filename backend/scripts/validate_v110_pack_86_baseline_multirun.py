#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_86_lobby_psp_ensure/v110_pack_86_baseline_multirun_v1.json')))
for k in ('baseline_pre_pack_run1','baseline_pre_pack_run2','baseline_pre_pack_run3'):
    r = d.get(k); assert r is not None
    assert r.get('required_fail') == 0
    assert r.get('miss') == 0
p1, p2, p3 = d['baseline_pre_pack_run1']['pass'], d['baseline_pre_pack_run2']['pass'], d['baseline_pre_pack_run3']['pass']
assert p1 == p2 == p3, f'baseline not deterministic: {p1}/{p2}/{p3}'
assert d.get('deterministic') is True
print(f'[v110 PACK_86_BASELINE_MULTIRUN] OK run1=run2=run3={p1} required=0 miss=0 deterministic=true')
