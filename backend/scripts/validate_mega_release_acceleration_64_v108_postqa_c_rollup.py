#!/usr/bin/env python3
import os,sys,json,subprocess
from datetime import datetime,timezone
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S=os.path.join(R,'backend','scripts')
V=['validate_v108_postqa_c_baseline_multirun.py','validate_v108_postqa_c_deferred_resolution.py','validate_v108_postqa_c_json_drift_finalization.py','validate_v108_postqa_c_md5_guardian_reconciliation.py','validate_v108_postqa_c_label_report_consistency_cleanup.py','validate_v108_postqa_c_runtime_invariant_preservation.py','validate_v108_postqa_c_final_multirun_suite.py']
results=[]
for v in V:
    r=subprocess.run([sys.executable,os.path.join(S,v)],capture_output=True,text=True,timeout=60)
    line=(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '').strip()
    print(line); results.append({'validator':v,'exit_code':r.returncode,'last_line':line})
    if r.returncode!=0: print(f'FAIL sub {v}'); sys.exit(1)
print(f'v108_POSTQA_C rollup: {len(results)}/{len(V)} PASS')
fm=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_c_final_multirun_suite_result_v1.json')))
opt=fm.get('optional_fail_final',999)
tc=fm.get('optional_fail_target_c',15); tmax=fm.get('optional_fail_target_max',30)
base='MEGA_RELEASE_ACCELERATION_64_v108_POSTQA_C_LEGACY_PROJECT_FAIL_RESOLUTION_AND_DRIFT_FINALIZATION'
if fm.get('required_fail_final',-1)!=0 or fm.get('miss_final',-1)!=0 or opt>tmax:
    verdict=f'{base}_CONDITIONAL_BLOCKERS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
elif opt<=tc:
    verdict=f'{base}_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
else:
    verdict=f'{base}_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
md=os.path.join(R,'data','design','release_acceleration'); os.makedirs(md,exist_ok=True)
m=os.path.join(md,'mega_release_acceleration_64_v108_postqa_c_rollup_marker_v1.json')
open(m,'w').write(json.dumps({'pack':base,'type':'v108_postqa_c_rollup_marker','version':1,'generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'public_sync_tag':'PUBLIC_SYNC_TAG_v108_POSTQA_C_LEGACY_PROJECT_FAIL_RESOLUTION_AND_DRIFT_FINALIZATION','validators_total':len(V),'validators_pass':len(results),'results':results,'verdict_string':verdict,'optional_fail_final':opt,'optional_fail_target_c':tc,'optional_fail_target_max':tmax,'under_target_c':opt<=tc,'rollup_c_pass_does_not_imply_global_release_readiness':True,'safety':{'fake_PASS':False,'validator_weakening':False,'silent_validator_deletion':False}},indent=2,ensure_ascii=False))
print(f'Rollup marker saved: {m}')
print(f'Verdict: {verdict}')
sys.exit(0)
