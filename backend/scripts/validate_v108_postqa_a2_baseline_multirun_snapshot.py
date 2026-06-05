#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_a2_baseline_multirun_snapshot_v1.json'),encoding='utf-8'))
if d.get('runs_executed',0)<3: print('FAIL runs<3'); sys.exit(1)
for r in d.get('runs') or []:
    if r.get('required_fail',-1)!=0: print('FAIL required>0'); sys.exit(1)
    if r.get('miss',-1)!=0: print('FAIL miss>0'); sys.exit(1)
if not d.get('deterministic',False): print('FAIL not deterministic'); sys.exit(1)
if len(d.get('intersection_fail') or [])<1: print('FAIL no intersection'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS — v108_POSTQA_A2 baseline multirun snapshot (3 run deterministic)'); sys.exit(0)
