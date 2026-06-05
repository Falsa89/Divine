#!/usr/bin/env python3
import os,sys,json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_a2_full_fail_triage_v1.json'),encoding='utf-8'))
fails=d.get('fails') or []
if len(fails)!=d.get('total_fail_count'): print('FAIL count mismatch'); sys.exit(1)
required_keys=['validator_id','validator_file','current_status','seen_in_runs','category','introduced_by_v108_postqa_a','root_cause','risk_level','action','action_pack','supersede_allowed']
allowed_categories={'preexisting_baseline','legacy_md5_guardian','auto_generated_json_drift','obsolete_validator','real_runtime_blocker','environmental','superseded_formally','unknown'}
allowed_actions={'keep_failing','formal_supersede','update_baseline_with_historical_reference','stabilize_generated_json','move_to_historical_suite','fix_runtime','defer_to_pack'}
for f in fails:
    for k in required_keys:
        if k not in f: print(f'FAIL missing key {k} in {f.get("validator_id")}'); sys.exit(1)
    if f['category'] not in allowed_categories: print(f'FAIL bad category {f["category"]}'); sys.exit(1)
    if f['action'] not in allowed_actions: print(f'FAIL bad action {f["action"]}'); sys.exit(1)
    if f['category']=='real_runtime_blocker' and f.get('supersede_allowed',False):
        print(f'FAIL real_runtime_blocker cannot be superseded: {f["validator_id"]}'); sys.exit(1)
saf=d.get('safety') or {}
for k in ('fake_PASS','validator_weakening','silent_validator_deletion','cosmetic_supersede_applied','runtime_p0_misclassified_as_drift'):
    if saf.get(k,True): print(f'FAIL {k}'); sys.exit(1)
print(f'PASS — v108_POSTQA_A2 full fail triage ({len(fails)} fails classified)'); sys.exit(0)
