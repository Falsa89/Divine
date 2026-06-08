#!/usr/bin/env python3
# Pack 81 - Track 15: final 3-run suite snapshot.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_81_user_heroes_server_scope/v110_pack_81_user_heroes_server_scope_summary_v1.json')
d = json.load(open(S))
f = d.get('final_post_pack', {})
assert f.get('required_fail') == 0
assert f.get('miss') == 0
delta = d.get('delta', {})
assert delta.get('pass', 0) >= 1
assert delta.get('required_fail', 0) == 0
print(f"[v110 PACK_81_FINAL_MULTIRUN_SUITE] OK final_pass={f.get('pass')} fail={f.get('fail')} required_fail=0 miss=0 delta_pass={delta.get('pass')}")
