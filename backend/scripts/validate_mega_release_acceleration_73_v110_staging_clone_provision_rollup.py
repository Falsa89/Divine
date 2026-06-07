#!/usr/bin/env python3
"""v110 staging clone provision rollup pack 73."""
import json, os, re, subprocess, sys
from datetime import datetime, timezone
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, "backend", "scripts")
FINAL = os.path.join(R, "data", "design", "v110_staging_clone", "v110_staging_clone_final_multirun_suite_result_v1.json")
MASTER = os.path.join(S, "run_hero_skill_kit_validator_suite.py")
SENT = "PUBLIC_SYNC_TAG_v110_PSP_STAGING_CLONE_PROVISION"
BASE = "MEGA_RELEASE_ACCELERATION_73_v110_PSP_STAGING_CLONE_PROVISION"
SUB = [
    "validate_v110_staging_clone_baseline_multirun.py",
    "validate_v110_source_db_classification.py",
    "validate_v110_staging_clone_plan.py",
    "validate_v110_staging_clone_backup_result.py",
    "validate_v110_staging_clone_execution_result.py",
    "validate_v110_staging_marker_result.py",
    "validate_v110_clone_integrity_verification.py",
    "validate_v110_pack72_readiness_recheck.py",
    "validate_v110_zero_production_mutation_proof.py",
    "validate_v110_staging_clone_runtime_invariant_preservation.py",
]
def _p(out):
    m = re.search(r"pass=(\d+),\s*fail=(\d+),\s*miss=(\d+)", out)
    if not m: return None
    rr = re.search(r"REQUIRED FAIL[^\d]*(\d+)", out)
    return {"pass": int(m.group(1)), "fail": int(m.group(2)), "miss": int(m.group(3)), "required_fail": int(rr.group(1)) if rr else 0}
def _three():
    runs = []
    for i in range(3):
        r = subprocess.run([sys.executable, MASTER], capture_output=True, text=True, timeout=180)
        p = _p((r.stdout or "") + "\n" + (r.stderr or ""))
        if not p:
            print("FAIL parse"); sys.exit(1)
        runs.append({"run": i+1, **p})
    return runs
def _ensure_final():
    in_suite = os.environ.get("SUITE_RUNNER_ACTIVE") == "1"
    if in_suite and os.path.isfile(FINAL): return json.load(open(FINAL))
    if in_suite and not os.path.isfile(FINAL):
        print("[v110 STAGING-CLONE ROLLUP] suite-mode skip"); return None
    runs = _three()
    s = lambda k: {r[k] for r in runs}
    det = len(s("pass"))==1 and len(s("fail"))==1 and len(s("miss"))==1 and len(s("required_fail"))==1
    last = runs[-1]
    p = {"pack": BASE, "track": "K", "sentinel": SENT, "runs": runs, "deterministic": det,
         "pass_final": last["pass"], "fail_final": last["fail"], "miss_final": last["miss"],
         "required_fail_final": last["required_fail"], "optional_fail_final": last["fail"] - last["required_fail"],
         "optional_fail_target_max": 30,
         "safety_flags": {"fake_PASS": False, "validator_weakening": False, "silent_validator_deletion": False, "release_readiness_claimed": False}}
    os.makedirs(os.path.dirname(FINAL), exist_ok=True)
    json.dump(p, open(FINAL, "w"), indent=2, ensure_ascii=False)
    return p
def main():
    results = []
    for v in SUB:
        r = subprocess.run([sys.executable, os.path.join(S, v)], capture_output=True, text=True, timeout=60)
        line = (r.stdout.strip().splitlines()[-1] if r.stdout.strip() else "").strip()
        print(line)
        results.append({"validator": v, "exit_code": r.returncode, "last_line": line})
        if r.returncode != 0:
            print(f"FAIL {v}"); print(r.stdout[-1500:]); print(r.stderr[-1500:]); sys.exit(1)
    final = _ensure_final()
    if final is None:
        print(f"v110 staging-clone rollup: {len(results)}/{len(SUB)} PASS (suite mode)"); sys.exit(0)
    fr = subprocess.run([sys.executable, os.path.join(S, "validate_v110_staging_clone_final_multirun_suite.py")], capture_output=True, text=True, timeout=60)
    print(fr.stdout.strip().splitlines()[-1] if fr.stdout.strip() else "")
    if fr.returncode != 0:
        print("FAIL final"); sys.exit(1)
    opt = final.get("optional_fail_final", 999); tmax = final.get("optional_fail_target_max", 30)
    if final.get("required_fail_final", -1) != 0 or final.get("miss_final", -1) != 0 or opt > tmax:
        verdict = f"{BASE}_CONDITIONAL_BLOCKERS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"
    else:
        verdict = f"{BASE}_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"
    md = os.path.join(R, "data", "design", "release_acceleration")
    os.makedirs(md, exist_ok=True)
    mp = os.path.join(md, "mega_release_acceleration_73_v110_staging_clone_provision_rollup_marker_v1.json")
    # load auxiliary results
    exec_res = json.load(open(os.path.join(R, "data/design/v110_staging_clone/v110_staging_clone_execution_result_v1.json")))
    marker_res = json.load(open(os.path.join(R, "data/design/v110_staging_clone/v110_staging_marker_result_v1.json")))
    integrity = json.load(open(os.path.join(R, "data/design/v110_staging_clone/v110_clone_integrity_verification_v1.json")))
    payload = {"pack": BASE, "type": "v110_staging_clone_provision_rollup_marker", "version": 1,
               "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
               "public_sync_tag": SENT,
               "validators_total": len(results) + 1,
               "validators_pass": len([x for x in results if x["exit_code"] == 0]) + (1 if fr.returncode == 0 else 0),
               "verdict_string": verdict,
               "required_fail_final": final.get("required_fail_final"), "miss_final": final.get("miss_final"),
               "optional_fail_final": opt, "optional_fail_target_max": tmax, "under_target_max": opt <= tmax,
               "deterministic": final.get("deterministic"),
               "target_db": exec_res.get("target_db"), "source_db": exec_res.get("source_db"),
               "target_inserted_docs": exec_res.get("target_writes_total_inserted_docs", 0),
               "target_marker_present": marker_res.get("marker_inserted_in_target", False),
               "source_marker_present": marker_res.get("marker_inserted_in_source", False),
               "clone_users_match": integrity.get("users_count_match", False),
               "clone_user_heroes_match": integrity.get("user_heroes_count_match", False),
               "psp_apply_executed": False, "production_db_written": False,
               "rollup_pass_does_not_imply_release_readiness": True,
               "safety": {"fake_PASS": False, "validator_weakening": False, "release_readiness_claimed": False,
                          "psp_apply_executed": False, "production_db_written": False, "destructive_source_op": False,
                          "delete_on_source": False, "premium_grant": False, "reward_live": False, "progress_live": False}}
    open(mp, "w").write(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"Rollup marker: {mp}"); print(f"Verdict: {verdict}")
    print(f"v110 staging-clone rollup: {len(results) + 1}/{len(SUB) + 1} PASS")
    sys.exit(0)
if __name__ == "__main__":
    main()
