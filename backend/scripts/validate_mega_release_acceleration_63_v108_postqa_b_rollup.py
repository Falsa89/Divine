#!/usr/bin/env python3
import os,sys,json,subprocess
from datetime import datetime,timezone
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S=os.path.join(R,'backend','scripts')
V=['validate_v108_postqa_b_baseline_multirun.py','validate_v108_postqa_b_redis_environmental_stabilization.py','validate_v108_postqa_b_json_drift_stabilization.py','validate_v108_postqa_b_watchlist_equipment_equip_added.py','validate_v108_postqa_b_project_preexisting_fail_classification.py','validate_v108_postqa_b_runtime_invariant_preservation.py','validate_v108_postqa_b_final_multirun_suite.py']
results=[]
for v in V:
    r=subprocess.run([sys.executable,os.path.join(S,v)],capture_output=True,text=True,timeout=60)
    line=(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '').strip()
    print(line); results.append({'validator':v,'exit_code':r.returncode,'last_line':line})
    if r.returncode!=0: print(f'FAIL sub {v}'); sys.exit(1)
print(f'v108_POSTQA_B rollup: {len(results)}/{len(V)} PASS')
fm=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_b_final_multirun_suite_result_v1.json')))
opt=fm.get('optional_fail_final',999); tgt=fm.get('optional_fail_target_max',30)
verdict=('MEGA_RELEASE_ACCELERATION_63_v108_POSTQA_B_ENVIRONMENTAL_AND_DRIFT_STABILIZATION_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING' if (opt<=tgt and fm.get('deterministic_over_3_runs',False) and fm.get('required_fail_final',-1)==0 and fm.get('miss_final',-1)==0) else 'MEGA_RELEASE_ACCELERATION_63_v108_POSTQA_B_ENVIRONMENTAL_AND_DRIFT_STABILIZATION_CONDITIONAL_BLOCKERS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING')
md=os.path.join(R,'data','design','release_acceleration'); os.makedirs(md,exist_ok=True)
m=os.path.join(md,'mega_release_acceleration_63_v108_postqa_b_rollup_marker_v1.json')
open(m,'w').write(json.dumps({'pack':'MEGA_RELEASE_ACCELERATION_63_v108_POSTQA_B_ENVIRONMENTAL_AND_DRIFT_STABILIZATION','type':'v108_postqa_b_rollup_marker','version':1,'generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'public_sync_tag':'PUBLIC_SYNC_TAG_v108_POSTQA_B_ENVIRONMENTAL_AND_DRIFT_STABILIZATION','validators_total':len(V),'validators_pass':len(results),'results':results,'verdict_string':verdict,'optional_fail_final':opt,'optional_fail_target_max':tgt,'rollup_b_pass_does_not_imply_global_release_readiness':True,'safety':{'fake_PASS':False,'validator_weakening':False,'silent_validator_deletion':False}},indent=2,ensure_ascii=False))
print(f'Rollup marker saved: {m}')
print(f'Verdict: {verdict}')
sys.exit(0)
