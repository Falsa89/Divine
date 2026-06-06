#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_c_deferred_resolution_v1.json')))
if d.get('total_items',0)<11: print('FAIL <11'); sys.exit(1)
allowed={'historical_guardian_documented','closed_by_runtime_fix','formal_supersede_with_replacement_invariant','superseded_via_b','obsolete_but_preserved'}
for r in d.get('resolutions') or []:
    if r.get('decision') not in allowed: print(f'FAIL bad decision {r.get("decision")}'); sys.exit(1)
    if not r.get('reason'): print(f'FAIL no reason {r.get("validator_id")}'); sys.exit(1)
if d.get('summary',{}).get('supersede_applied',-1)!=0: print('FAIL supersede>0'); sys.exit(1)
if d.get('summary',{}).get('deletions_applied',-1)!=0: print('FAIL deletions>0'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion','cosmetic_supersede'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print(f'PASS — v108_POSTQA_C deferred resolution ({d.get("total_items")} items)'); sys.exit(0)
