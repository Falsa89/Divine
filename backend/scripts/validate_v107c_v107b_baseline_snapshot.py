#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','battle_launch','v107c_v107b_baseline_snapshot_v1.json')
if not os.path.isfile(p): print('FAIL'); sys.exit(1)
d=json.load(open(p,encoding='utf-8'))
art=d.get('v107b_artifacts_present') or {}
if len(art)<6: print(f'FAIL artifacts<6'); sys.exit(1)
for f,pres in art.items():
    if pres and not os.path.exists(os.path.join(R,f)): print(f'FAIL missing {f}'); sys.exit(1)
if d.get('v107b_smoke_cases_pass')!=3 or d.get('v107b_smoke_cases_total')!=3: print('FAIL smoke counts'); sys.exit(1)
if d.get('v107b_db_writes_performed',-1)!=0: print('FAIL db_writes'); sys.exit(1)
print('PASS \u2014 v107C v107B baseline snapshot (6 artifacts, smoke 3/3)'); sys.exit(0)
