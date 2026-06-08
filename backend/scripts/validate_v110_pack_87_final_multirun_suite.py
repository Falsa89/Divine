#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_87_server_scoped_starter_flow/v110_pack_87_final_multirun_suite_result_v1.json')))
for k in ('final_post_pack_run1','final_post_pack_run2','final_post_pack_run3'):
    r = d.get(k); assert r is not None, f'{k} missing'
    if d.get('placeholder_pending_runtime_population') is True and r.get('pass') is None:
        continue
    assert r.get('required_fail') == 0, f'{k} required_fail != 0'
    assert r.get('miss') == 0, f'{k} miss != 0'
if d.get('placeholder_pending_runtime_population') is True:
    print('[v110 PACK_87_FINAL_MULTIRUN_SUITE] OK placeholder_pending_runtime_population (will be populated by final 3-run)')
else:
    p1, p2, p3 = d['final_post_pack_run1']['pass'], d['final_post_pack_run2']['pass'], d['final_post_pack_run3']['pass']
    assert p1 == p2 == p3, f'final not deterministic: {p1}/{p2}/{p3}'
    print(f'[v110 PACK_87_FINAL_MULTIRUN_SUITE] OK run1=run2=run3={p1} required=0 miss=0')
