#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_c_final_multirun_suite_result_v1.json')))
if not d.get('deterministic_over_3_runs',False): print('FAIL not deterministic'); sys.exit(1)
if d.get('required_fail_final',-1)!=0: print('FAIL required'); sys.exit(1)
if d.get('miss_final',-1)!=0: print('FAIL miss'); sys.exit(1)
if d.get('optional_fail_final',999)>d.get('optional_fail_target_max',30): print('FAIL optional>max target'); sys.exit(1)
if d.get('runtime_invariant_validators_pass',0)<10: print('FAIL invariants'); sys.exit(1)
if not d.get('runtime_invariant_rollup_pass',False): print('FAIL rollup'); sys.exit(1)
if not d.get('v108_postqa_a2_rollup_pass',False) or not d.get('v108_postqa_b_rollup_pass',False) or not d.get('v108_postqa_c_rollup_pass',False): print('FAIL rollup chain'); sys.exit(1)
print(f'PASS — v108_POSTQA_C final multirun ({d.get("optional_fail_final")}/{d.get("optional_fail_target_max")} optional, target_c={d.get("optional_fail_target_c")} under={d.get("under_target_c")})'); sys.exit(0)
