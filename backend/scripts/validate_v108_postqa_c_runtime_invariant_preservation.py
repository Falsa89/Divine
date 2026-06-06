#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_c_runtime_invariant_preservation_v1.json')))
if d.get('runtime_invariant_validators_present_and_registered',0)<10: print('FAIL invariants<10'); sys.exit(1)
if not d.get('runtime_invariant_rollup_pass',False): print('FAIL rollup'); sys.exit(1)
if 'CONDITIONAL_BLOCKERS' not in (d.get('v108_POSTQA_A_rollup_marker_verdict') or ''): print('FAIL verdict_a drift'); sys.exit(1)
for k in ('any_invariant_deleted','any_invariant_downgraded','rollup_marker_claims_ready_falsely'):
    if d.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS — v108_POSTQA_C runtime invariant preservation'); sys.exit(0)
