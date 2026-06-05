#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v108_pre_v107d_baseline_snapshot_v1.json')
d=json.load(open(p,encoding='utf-8'))
b=d.get('suite_baseline_pre') or {}
if b.get('pass')!=1115 or b.get('fail')!=23 or b.get('miss')!=0 or b.get('required_fail')!=0: print('FAIL baseline'); sys.exit(1)
if d.get('v107d_validators_count')!=10 or d.get('v107d_validators_pass')!=10: print('FAIL v107d count'); sys.exit(1)
for k in ('pre_battle_lobby_binding_present','combat_tsx_untouched_by_v107d','story_tsx_untouched_by_v107d'):
    if not d.get(k,False): print(f'FAIL {k}'); sys.exit(1)
for f in (d.get('v107d_final_report_path'), d.get('v107d_rollup_marker_path')):
    if not os.path.isfile(os.path.join(R,f or '')): print(f'FAIL missing {f}'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS — v108_pre v107D baseline snapshot'); sys.exit(0)
