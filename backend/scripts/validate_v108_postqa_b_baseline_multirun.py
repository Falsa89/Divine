#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_b_baseline_multirun_v1.json')))
if d.get('baseline_post_redis_install',{}).get('required_fail',-1)!=0: print('FAIL required>0'); sys.exit(1)
if d.get('baseline_post_redis_install',{}).get('miss',-1)!=0: print('FAIL miss>0'); sys.exit(1)
if not d.get('a2_1_artifacts_coherent',False): print('FAIL a2_1 not coherent'); sys.exit(1)
if not d.get('runtime_invariant_10_pass',False): print('FAIL invariants<10'); sys.exit(1)
print('PASS — v108_POSTQA_B baseline multirun'); sys.exit(0)
