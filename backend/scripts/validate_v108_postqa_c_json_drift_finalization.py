#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_c_json_drift_finalization_v1.json')))
if d.get('substantive_fields_ignored'): print('FAIL substantive ignored'); sys.exit(1)
if d.get('validators_changed_to_always_pass'): print('FAIL changed to always pass'); sys.exit(1)
if d.get('behavior_changed_but_marked_pass',True): print('FAIL behavior changed marked pass'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion','hiding_fail_from_suite'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS — v108_POSTQA_C json drift finalization (deferred onestamente)'); sys.exit(0)
