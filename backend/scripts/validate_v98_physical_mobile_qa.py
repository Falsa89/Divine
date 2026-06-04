#!/usr/bin/env python3
"""v98 — Physical mobile QA."""
import os, sys, json
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(ROOT,'data','design','closed_alpha','v98_physical_mobile_qa_result_v1.json')
if not os.path.isfile(p): print('FAIL — file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d=json.load(f)
if d.get('android_physical',{}).get('status') not in ('PASS','MANUAL_QA_REQUIRED'): print('FAIL — android'); sys.exit(1)
if d.get('ios_physical',{}).get('status') not in ('PASS','MANUAL_QA_REQUIRED'): print('FAIL — ios'); sys.exit(1)
if not d.get('no_fake_pass'): print('FAIL — no_fake_pass'); sys.exit(1)
local=d.get('local_smoke_verified') or {}
for k in ('auth_session','refresh_rotation','data_export','privacy_status','formation_fetch'):
    if not local.get(k): print(f'FAIL — local_smoke.{k}'); sys.exit(1)
if local.get('battle_engine_smoke')!='21/21 PASS': print('FAIL — battle_engine smoke'); sys.exit(1)
cl=d.get('manual_qa_checklist') or []
if len(cl)<2: print('FAIL — manual_qa_checklist too short'); sys.exit(1)
print('PASS — v98 physical mobile QA (honest manual required)')
sys.exit(0)
