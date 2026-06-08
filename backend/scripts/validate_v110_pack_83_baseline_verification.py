#!/usr/bin/env python3
# Pack 83 - Track A: baseline 3-run verification.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_psp_normalization_preflight/v110_psp_normalization_preflight_summary_v1.json')
d = json.load(open(S))
b = d.get('baseline_pre_pack', {})
assert b.get('required_fail') == 0
assert b.get('miss') == 0
assert b.get('pass', 0) > 1300
assert b.get('fail', 100) <= 30, f'baseline OPTIONAL FAIL>30: {b}'
print(f"[v110 PACK_83_BASELINE_VERIFICATION] OK pass={b.get('pass')} fail={b.get('fail')} required=0 miss=0")
