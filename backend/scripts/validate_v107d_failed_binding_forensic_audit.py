#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p=os.path.join(R,'data','design','closed_alpha','v107d_failed_binding_forensic_audit_v1.json')
d=json.load(open(p,encoding='utf-8'))
if len(d.get('validators_triggered_by_combat_tsx_change') or [])<10: print('FAIL'); sys.exit(1)
if not d.get('v107D_hypothesis') or not d.get('v107D_test') or not d.get('conclusion'): print('FAIL'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS \u2014 v107D failed binding forensic audit'); sys.exit(0)
