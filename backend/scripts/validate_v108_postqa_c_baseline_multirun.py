#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_c_baseline_multirun_v1.json')))
if d.get('baseline',{}).get('required_fail',-1)!=0: print('FAIL required'); sys.exit(1)
if d.get('baseline',{}).get('miss',-1)!=0: print('FAIL miss'); sys.exit(1)
if not d.get('runtime_invariant_10_pass',False): print('FAIL invariants'); sys.exit(1)
print('PASS — v108_POSTQA_C baseline multirun'); sys.exit(0)
