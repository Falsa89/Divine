#!/usr/bin/env python3
# Pack 80 — Track L: final 3-run suite snapshot (sintetico).
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_80_lobby_fetch/v110_pack_80_lobby_fetch_summary_v1.json')
d = json.load(open(S))
f = d.get('final_post_pack', {})
assert f.get('required_fail') == 0, 'REQUIRED FAIL must be 0 in final'
assert f.get('miss') == 0, 'MISS must be 0 in final'
b = d.get('baseline_pre_pack', {})
delta = d.get('delta', {})
assert delta.get('pass', 0) >= 1, 'expected >=1 new PASS from new validators'
assert delta.get('required_fail', 0) == 0, 'no new required fails allowed'
print(f"[v110 LOBBY_TEAM_FETCH_FINAL_MULTIRUN_SUITE] OK final_pass={f.get('pass')} fail={f.get('fail')} required_fail=0 miss=0 delta_pass={delta.get('pass')}")
