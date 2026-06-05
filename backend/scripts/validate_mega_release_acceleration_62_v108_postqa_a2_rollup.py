#!/usr/bin/env python3
import os,sys,json,subprocess
from datetime import datetime,timezone
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S=os.path.join(R,'backend','scripts')
V=['validate_v108_postqa_a2_baseline_multirun_snapshot.py','validate_v108_postqa_a2_full_fail_triage.py','validate_v108_postqa_a2_runtime_invariant_preservation.py','validate_v108_postqa_a2_md5_historical_reconciliation.py','validate_v108_postqa_a2_auto_generated_json_drift_stabilization.py','validate_v108_postqa_a2_watchlist_roadmap_preservation.py','validate_v108_postqa_a2_final_multirun_suite_result.py']
results=[]
for v in V:
    r=subprocess.run([sys.executable,os.path.join(S,v)],capture_output=True,text=True,timeout=60)
    line=(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else '').strip()
    print(line); results.append({'validator':v,'exit_code':r.returncode,'last_line':line})
    if r.returncode!=0: print(f'FAIL sub {v}'); sys.exit(1)
print(f'v108_POSTQA_A2 rollup: {len(results)}/{len(V)} PASS')
# Determine verdict from final multirun result
fm=json.load(open(os.path.join(R,'data','design','postqa','v108_postqa_a2_final_multirun_suite_result_v1.json'),encoding='utf-8'))
opt=fm.get('optional_fail_final',999); tgt=fm.get('optional_fail_target_max',30)
if opt<=tgt and fm.get('deterministic_over_3_runs',False) and fm.get('required_fail_final',-1)==0 and fm.get('miss_final',-1)==0:
    verdict='MEGA_RELEASE_ACCELERATION_62_v108_POSTQA_A2_LEGACY_FAIL_TRIAGE_AND_BASELINE_RECONCILIATION_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
else:
    verdict='MEGA_RELEASE_ACCELERATION_62_v108_POSTQA_A2_LEGACY_FAIL_TRIAGE_AND_BASELINE_RECONCILIATION_CONDITIONAL_BLOCKERS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING'
md=os.path.join(R,'data','design','release_acceleration'); os.makedirs(md,exist_ok=True)
m=os.path.join(md,'mega_release_acceleration_62_v108_postqa_a2_rollup_marker_v1.json')
open(m,'w',encoding='utf-8').write(json.dumps({'pack':'MEGA_RELEASE_ACCELERATION_62_v108_POSTQA_A2_LEGACY_FAIL_TRIAGE_AND_BASELINE_RECONCILIATION','type':'v108_postqa_a2_rollup_marker','version':1,'generated_at_utc':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'public_sync_tag':'PUBLIC_SYNC_TAG_v108_POSTQA_A2_LEGACY_FAIL_TRIAGE_AND_BASELINE_RECONCILIATION','validators_total':len(V),'validators_pass':len(results),'results':results,'verdict_string':verdict,'optional_fail_final':opt,'optional_fail_target_max':tgt,'deterministic_over_3_runs':fm.get('deterministic_over_3_runs',False),'runtime_invariant_validators_pass':fm.get('runtime_invariant_validators_pass',0),'rollup_a2_pass_does_not_imply_global_release_readiness':True,'safety':{'fake_PASS':False,'validator_weakening':False,'silent_validator_deletion':False,'cosmetic_supersede_applied':False}},indent=2,ensure_ascii=False))
print(f'Rollup marker saved: {m}')
print(f'Verdict: {verdict}')
sys.exit(0)
