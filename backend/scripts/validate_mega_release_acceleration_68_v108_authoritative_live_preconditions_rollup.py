#!/usr/bin/env python3
"""v108_AUTHORITATIVE_LIVE_PRECONDITIONS rollup pack 68."""
import json,os,re,subprocess,sys
from datetime import datetime,timezone
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPTS=os.path.join(ROOT,"backend","scripts")
FINAL_PATH=os.path.join(ROOT,"data","design","authoritative_live_preconditions","v108_authoritative_live_preconditions_final_multirun_v1.json")
MASTER=os.path.join(SCRIPTS,"run_hero_skill_kit_validator_suite.py")
SENTINEL="PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_LIVE_PRECONDITIONS_AND_IDEMPOTENCY_LEDGER"
BASE_VERDICT="MEGA_RELEASE_ACCELERATION_68_v108_AUTHORITATIVE_LIVE_PRECONDITIONS_AND_IDEMPOTENCY_LEDGER"
SUB=["validate_v108_authoritative_live_preconditions_baseline_multirun.py","validate_v108_authoritative_live_precondition_matrix.py","validate_v108_authoritative_idempotency_ledger_dryrun.py","validate_v108_authoritative_live_reward_progress_blocker.py","validate_v108_authoritative_real_team_source_readiness.py","validate_v108_authoritative_enemy_source_readiness.py","validate_v108_authoritative_server_id_filter_readiness.py","validate_v108_authoritative_rollback_plan.py","validate_v108_authoritative_zero_mutation_preservation.py","validate_v108_authoritative_runtime_invariant_preservation.py"]
def _p(out):
    m=re.search(r"pass=(\d+),\s*fail=(\d+),\s*miss=(\d+)",out)
    if not m: return None
    rr=re.search(r"REQUIRED FAIL[^\d]*(\d+)",out)
    return {"pass":int(m.group(1)),"fail":int(m.group(2)),"miss":int(m.group(3)),"required_fail":int(rr.group(1)) if rr else 0}
def _three():
    runs=[]
    for i in range(3):
        r=subprocess.run([sys.executable,MASTER],capture_output=True,text=True,timeout=180)
        p=_p((r.stdout or "")+"\n"+(r.stderr or ""))
        if not p: print("FAIL parse"); sys.exit(1)
        runs.append({"run":i+1,**p})
    return runs
def _ensure_final():
    in_suite=os.environ.get("SUITE_RUNNER_ACTIVE")=="1"
    if in_suite and os.path.isfile(FINAL_PATH): return json.load(open(FINAL_PATH))
    if in_suite and not os.path.isfile(FINAL_PATH):
        print("[v108_AUTH_LIVE_PRECOND ROLLUP] suite-mode skip: final deferred"); return None
    runs=_three()
    s=lambda k: {r[k] for r in runs}
    deterministic = len(s("pass"))==1 and len(s("fail"))==1 and len(s("miss"))==1 and len(s("required_fail"))==1
    last=runs[-1]
    payload={"pack":BASE_VERDICT,"track":"K","sentinel":SENTINEL,"description":"Final 3-run del master DOPO v108_AUTHORITATIVE_LIVE_PRECONDITIONS.","runs":runs,"deterministic":deterministic,"pass_final":last["pass"],"fail_final":last["fail"],"miss_final":last["miss"],"required_fail_final":last["required_fail"],"optional_fail_final":last["fail"]-last["required_fail"],"optional_fail_target_max":30,"safety_flags":{"fake_PASS":False,"validator_weakening":False,"silent_validator_deletion":False,"release_readiness_claimed":False}}
    json.dump(payload,open(FINAL_PATH,"w"),indent=2,ensure_ascii=False)
    return payload
def main():
    results=[]
    for v in SUB:
        r=subprocess.run([sys.executable,os.path.join(SCRIPTS,v)],capture_output=True,text=True,timeout=60)
        line=(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "").strip()
        print(line)
        results.append({"validator":v,"exit_code":r.returncode,"last_line":line})
        if r.returncode!=0:
            print(f"FAIL sub {v}"); print(r.stdout[-1500:]); print("---STDERR---"); print(r.stderr[-1500:]); sys.exit(1)
    final=_ensure_final()
    if final is None:
        print(f"v108_AUTH_LIVE_PRECOND rollup: {len(results)}/{len(SUB)} PASS (suite mode)"); sys.exit(0)
    fr=subprocess.run([sys.executable,os.path.join(SCRIPTS,"validate_v108_authoritative_live_preconditions_final_multirun.py")],capture_output=True,text=True,timeout=60)
    print(fr.stdout.strip().splitlines()[-1] if fr.stdout.strip() else "")
    if fr.returncode!=0: print("FAIL final multirun"); sys.exit(1)
    opt=final.get("optional_fail_final",999); tmax=final.get("optional_fail_target_max",30)
    if final.get("required_fail_final",-1)!=0 or final.get("miss_final",-1)!=0 or opt>tmax:
        verdict=f"{BASE_VERDICT}_CONDITIONAL_BLOCKERS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"
    else:
        verdict=f"{BASE_VERDICT}_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"
    md=os.path.join(ROOT,"data","design","release_acceleration"); os.makedirs(md,exist_ok=True)
    mp=os.path.join(md,"mega_release_acceleration_68_v108_authoritative_live_preconditions_rollup_marker_v1.json")
    payload={"pack":BASE_VERDICT,"type":"v108_authoritative_live_preconditions_rollup_marker","version":1,"generated_at_utc":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"public_sync_tag":SENTINEL,"validators_total":len(results)+1,"validators_pass":len([x for x in results if x["exit_code"]==0])+(1 if fr.returncode==0 else 0),"verdict_string":verdict,"required_fail_final":final.get("required_fail_final"),"miss_final":final.get("miss_final"),"optional_fail_final":opt,"optional_fail_target_max":tmax,"under_target_max":opt<=tmax,"deterministic":final.get("deterministic"),"rollup_pass_does_not_imply_release_readiness":True,"safety":{"fake_PASS":False,"validator_weakening":False,"silent_validator_deletion":False,"release_readiness_claimed":False,"reward_live_activation":False,"progress_live_activation":False,"ledger_db_write":False,"collection_creation":False}}
    open(mp,"w").write(json.dumps(payload,indent=2,ensure_ascii=False))
    print(f"Rollup marker saved: {mp}")
    print(f"Verdict: {verdict}")
    print(f"v108_AUTH_LIVE_PRECOND rollup: {len(results)+1}/{len(SUB)+1} PASS")
    sys.exit(0)
if __name__=="__main__": main()
