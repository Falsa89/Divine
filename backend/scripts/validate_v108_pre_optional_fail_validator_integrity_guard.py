#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v108_pre_optional_fail_validator_integrity_guard_v1.json')
d=json.load(open(p,encoding='utf-8'))
if d.get('baseline_pre_v108_pre')!=23: print('FAIL baseline_pre'); sys.exit(1)
if d.get('baseline_post_v108_pre',999)>30: print('FAIL baseline_post>30'); sys.exit(1)
if d.get('target_max',0)!=30: print('FAIL target'); sys.exit(1)
if d.get('required_fail_post',-1)!=0: print('FAIL required_post'); sys.exit(1)
if d.get('miss_post',-1)!=0: print('FAIL miss_post'); sys.exit(1)
for k in ('silent_validator_deletion','validator_weakening','hiding_optional_fails'):
    if d.get(k,True): print(f'FAIL {k}'); sys.exit(1)
if not d.get('md5_supersede_formal_proof_present',False): print('FAIL md5_proof'); sys.exit(1)
if not os.path.isfile(os.path.join(R,d.get('md5_supersede_proof_file',''))): print('FAIL proof_file missing'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion','hiding_optional_fails'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS — v108_pre optional fail / validator integrity guard'); sys.exit(0)
