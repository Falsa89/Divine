#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_b_final_multirun_suite_result_v1.json')))
if not d.get('deterministic_over_3_runs',False): print('FAIL not deterministic'); sys.exit(1)
if d.get('required_fail_final',-1)!=0: print('FAIL required>0'); sys.exit(1)
if d.get('miss_final',-1)!=0: print('FAIL miss>0'); sys.exit(1)
if d.get('optional_fail_final',999)>d.get('optional_fail_target_max',30):
    print(f'FAIL optional_fail_final={d.get("optional_fail_final")} > {d.get("optional_fail_target_max")}'); sys.exit(1)
if d.get('runtime_invariant_validators_pass',0)<10: print('FAIL invariants<10'); sys.exit(1)
if not d.get('runtime_invariant_rollup_pass',False): print('FAIL rollup_a pass'); sys.exit(1)
if not d.get('v108_postqa_a2_rollup_pass',False): print('FAIL a2 rollup'); sys.exit(1)
if not d.get('v108_postqa_b_validators_pass',False): print('FAIL b validators'); sys.exit(1)
print(f'PASS — v108_POSTQA_B final multirun ({d.get("optional_fail_final")}/{d.get("optional_fail_target_max")} optional, 3 run deterministic)'); sys.exit(0)
