#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_execute/v110_psp_normalization_execute_summary_v1.json')))
b = d.get('baseline_pre_pack', {})
assert b.get('required_fail') == 0 and b.get('miss') == 0 and b.get('pass', 0) > 1300
print(f"[v110 PACK_84_BASELINE_VERIFICATION] OK pass={b.get('pass')} fail={b.get('fail')} required=0 miss=0")
