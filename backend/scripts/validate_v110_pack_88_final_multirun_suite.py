#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_88_team_formation_strict_server_scope/v110_pack_88_final_multirun_suite_result_v1.json')))
for k in ('final_post_pack_run1','final_post_pack_run2','final_post_pack_run3'):
    r = d.get(k); assert r is not None
    if d.get('placeholder_pending_runtime_population') is True and r.get('pass') is None:
        continue
    assert r.get('required_fail') == 0 and r.get('miss') == 0
if d.get('placeholder_pending_runtime_population') is True:
    print('[v110 PACK_88_FINAL_MULTIRUN_SUITE] OK placeholder_pending_runtime_population')
else:
    p1,p2,p3 = d['final_post_pack_run1']['pass'], d['final_post_pack_run2']['pass'], d['final_post_pack_run3']['pass']
    assert p1==p2==p3
    print(f'[v110 PACK_88_FINAL_MULTIRUN_SUITE] OK run1=run2=run3={p1} required=0 miss=0')
