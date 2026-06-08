#!/usr/bin/env python3
# Pack 83 - Track N: final 3-run suite snapshot.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_psp_normalization_preflight/v110_psp_normalization_preflight_summary_v1.json')
d = json.load(open(S))
for k in ('final_post_pack_run1', 'final_post_pack_run2', 'final_post_pack_run3'):
    r = d.get(k); assert r is not None, f'{k} missing'
    assert r.get('required_fail') == 0
    assert r.get('miss') == 0
p1, p2, p3 = d['final_post_pack_run1']['pass'], d['final_post_pack_run2']['pass'], d['final_post_pack_run3']['pass']
assert p1 == p2 == p3, f'3-run not deterministic: {p1} {p2} {p3}'
f = d.get('final_post_pack', {})
assert f.get('required_fail') == 0
assert f.get('miss') == 0
delta = d.get('delta', {})
assert delta.get('required_fail', 0) == 0
assert delta.get('pass', 0) >= 1
print(f'[v110 PACK_83_FINAL_3RUN_SUITE] OK run1=run2=run3={p1} fail={f.get("fail")} required=0 miss=0 delta_pass={delta.get("pass")}')
