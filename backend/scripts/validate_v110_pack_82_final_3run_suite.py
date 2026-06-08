#!/usr/bin/env python3
# Pack 82 - Track 11: final 3-run suite snapshot (verifica 3 run espliciti).
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_82_psp_dual_read_compat/v110_pack_82_psp_dual_read_compat_summary_v1.json')
d = json.load(open(S))
# Pack 81 ha avuto solo 2 run dichiarati: Pack 82 DEVE averne 3 espliciti
for k in ('final_post_pack_run1', 'final_post_pack_run2', 'final_post_pack_run3'):
    r = d.get(k)
    assert r is not None, f'{k} missing - Pack 82 must document 3 explicit runs'
    assert r.get('required_fail') == 0, f'{k} required_fail must be 0'
    assert r.get('miss') == 0, f'{k} miss must be 0'
# Deterministicita': i 3 run devono dare lo stesso pass count
p1, p2, p3 = d['final_post_pack_run1']['pass'], d['final_post_pack_run2']['pass'], d['final_post_pack_run3']['pass']
assert p1 == p2 == p3, f'3-run not deterministic: {p1} {p2} {p3}'
f = d.get('final_post_pack', {})
assert f.get('required_fail') == 0
delta = d.get('delta', {})
assert delta.get('required_fail', 0) == 0
assert delta.get('pass', 0) >= 1
print(f'[v110 PACK_82_FINAL_3RUN_SUITE] OK run1=run2=run3={p1} fail={f.get("fail")} required_fail=0 miss=0 delta_pass={delta.get("pass")}')
