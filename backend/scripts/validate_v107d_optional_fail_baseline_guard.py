#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','closed_alpha','v107d_optional_fail_baseline_guard_v1.json')
d=json.load(open(p,encoding='utf-8'))
if d.get('baseline_pre_v107d')!=23 or d.get('baseline_post_v107d')!=23: print('FAIL baseline'); sys.exit(1)
if d.get('target_max',0)!=30: print('FAIL target'); sys.exit(1)
if not d.get('baseline_preserved',False): print('FAIL preserved'); sys.exit(1)
for k in ('silent_validator_deletion','validator_weakening','hiding_optional_fails'):
    if d.get(k,True): print(f'FAIL {k}'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion','hiding_optional_fails'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS \u2014 v107D optional fail baseline guard (23/23 preserved)'); sys.exit(0)
