#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_85_psp_onboarding/v110_pack_85_psp_onboarding_summary_v1.json')))
for k in ('final_post_pack_run1','final_post_pack_run2','final_post_pack_run3'):
    r = d.get(k); assert r is not None
    assert r.get('required_fail') == 0 and r.get('miss') == 0
p1, p2, p3 = d['final_post_pack_run1']['pass'], d['final_post_pack_run2']['pass'], d['final_post_pack_run3']['pass']
assert p1 == p2 == p3
delta = d.get('delta', {})
assert delta.get('required_fail', 0) == 0 and delta.get('pass', 0) >= 1
print(f'[v110 PACK_85_FINAL_3RUN_SUITE] OK run1=run2=run3={p1} delta_pass={delta.get("pass")}')
