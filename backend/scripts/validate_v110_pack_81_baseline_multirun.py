#!/usr/bin/env python3
# Pack 81 - Track 1: baseline 3-run suite snapshot (legge il summary).
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_81_user_heroes_server_scope/v110_pack_81_user_heroes_server_scope_summary_v1.json')
d = json.load(open(S))
b = d.get('baseline_pre_pack', {})
assert b.get('required_fail') == 0
assert b.get('miss') == 0
assert b.get('pass', 0) > 1300
print(f"[v110 PACK_81_BASELINE_MULTIRUN] OK pass={b.get('pass')} fail={b.get('fail')} required_fail=0 miss=0")
