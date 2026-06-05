#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107b_v107a_baseline_snapshot_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 missing'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
art=d.get('v107a_artifacts_present') or {}
if len(art)<10: print(f'FAIL \u2014 v107a artifacts < 10 (got {len(art)})'); sys.exit(1)
for f,pres in art.items():
    if pres and not os.path.exists(os.path.join(R,f)): print(f'FAIL \u2014 missing: {f}'); sys.exit(1)
if d.get('v107a_db_writes_performed',-1)!=0: print('FAIL \u2014 v107a db_writes must be 0'); sys.exit(1)
if d.get('v107a_endpoint_status')!='PREVIEW_ECHO_NON_AUTHORITATIVE': print('FAIL \u2014 endpoint status wrong'); sys.exit(1)
print(f"PASS \u2014 v107B v107A baseline snapshot ({len(art)} artifacts verified)"); sys.exit(0)
