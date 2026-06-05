#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_a2_auto_generated_json_drift_stabilization_v1.json'),encoding='utf-8'))
if d.get('generated_files_deleted'): print('FAIL generated_files_deleted'); sys.exit(1)
if d.get('validators_changed_to_always_pass'): print('FAIL validators_changed_to_always_pass'); sys.exit(1)
if d.get('behavior_changed_but_marked_pass',True): print('FAIL behavior_changed_but_marked_pass'); sys.exit(1)
if d.get('substantive_fields_ignored'): print('FAIL substantive_fields_ignored not empty'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion','hiding_fail_from_suite'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print('PASS — v108_POSTQA_A2 auto-generated JSON drift stabilization (no substantive change, no fake pass)'); sys.exit(0)
