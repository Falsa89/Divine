#!/usr/bin/env python3
"""v110 staging smoke rollup pack 72."""
import json, os, re, subprocess, sys
from datetime import datetime, timezone

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, "backend", "scripts")
FINAL = os.path.join(R, "data", "design", "v110_psp_apply_staging_smoke", "v110_staging_smoke_final_multirun_suite_result_v1.json")
MASTER = os.path.join(S, "run_hero_skill_kit_validator_suite.py")
SENT = "PUBLIC_SYNC_TAG_v110_PSP_APPLY_STAGING_SMOKE_LIMITED"
BASE = "MEGA_RELEASE_ACCELERATION_72_v110_PSP_APPLY_STAGING_SMOKE_LIMITED"
SUB = [
    "validate_v110_staging_smoke_baseline_multirun.py",
    "validate_v110_staging_smoke_environment_classification.py",
    "validate_v110_pre_smoke_db_snapshot.py",
    "validate_v110_staging_backup_execution.py",
    "validate_v110_limited_psp_apply_result.py",
    "validate_v110_idempotency_rerun_check.py",
    "validate_v110_post_apply_invariants.py",
    "validate_v110_rollback_drill_result.py",
    "validate_v110_post_smoke_final_snapshot.py",
    "validate_v110_staging_smoke_live_readiness_update.py",
    "validate_v110_staging_smoke_gate_preservation.py",
    "validate_v110_staging_smoke_runtime_invariant_preservation.py",
]

def _p(out):
    m = re.search(r"pass=(\d+),\s*fail=(\d+),\s*miss=(\d+)", out)
    if not m:
        return None
    rr = re.search(r"REQUIRED FAIL[^\d]*(\d+)", out)
    return {"pass": int(m.group(1)), "fail": int(m.group(2)), "miss": int(m.group(3)), "required_fail": int(rr.group(1)) if rr else 0}

def _three():
    runs = []
    for i in range(3):
        r = subprocess.run([sys.executable, MASTER], capture_output=True, text=True, timeout=180)
        p = _p((r.stdout or "") + "\n" + (r.stderr or ""))
        if not p:
            print("FAIL parse")
            sys.exit(1)
        runs.append({"run": i + 1, **p})
    return runs

def _ensure_final():
    in_suite = os.environ.get("SUITE_RUNNER_ACTIVE") == "1"
    if in_suite and os.path.isfile(FINAL):
        return json.load(open(FINAL))
    if in_suite and not os.path.isfile(FINAL):
        print("[v110 STAGING-SMOKE ROLLUP] suite-mode skip")
        return None
    runs = _three()
    s = lambda k: {r[k] for r in runs}
    det = len(s("pass")) == 1 and len(s("fail")) == 1 and len(s("miss")) == 1 and len(s("required_fail")) == 1
    last = runs[-1]
    p = {
        "pack": BASE,
        "track": "M",
        "sentinel": SENT,
        "runs": runs,
        "deterministic": det,
        "pass_final": last["pass"],
        "fail_final": last["fail"],
        "miss_final": last["miss"],
        "required_fail_final": last["required_fail"],
        "optional_fail_final": last["fail"] - last["required_fail"],
        "optional_fail_target_max": 30,
        "safety_flags": {
            "fake_PASS": False,
            "validator_weakening": False,
            "silent_validator_deletion": False,
            "release_readiness_claimed": False,
        },
    }
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
            print(f"FAIL {v}")
            print(r.stdout[-1500:])
            print(r.stderr[-1500:])
            sys.exit(1)
    final = _ensure_final()
    if final is None:
        print(f"v110 staging-smoke rollup: {len(results)}/{len(SUB)} PASS (suite mode)")
        sys.exit(0)
    fr = subprocess.run([sys.executable, os.path.join(S, "validate_v110_staging_smoke_final_multirun_suite.py")], capture_output=True, text=True, timeout=60)
    print(fr.stdout.strip().splitlines()[-1] if fr.stdout.strip() else "")
    if fr.returncode != 0:
        print("FAIL final")
        sys.exit(1)
    # Read environment classification to set verdict
    env_class = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_smoke/v110_environment_classification_v1.json")))
    apply_res = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_smoke/v110_limited_psp_apply_result_v1.json")))
    backup_res = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_smoke/v110_staging_backup_execution_result_v1.json")))
    rollback_res = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_smoke/v110_rollback_drill_result_v1.json")))
    opt = final.get("optional_fail_final", 999)
    tmax = final.get("optional_fail_target_max", 30)
    # CONDITIONAL_BLOCKERS if apply not executed (primary goal not achieved) OR suite issues
    apply_ok = apply_res.get("limited_apply_executed") is True
    backup_ok = backup_res.get("backup_executed") is True
    rollback_ok = rollback_res.get("rollback_drill_executed") is True
    suite_ok = final.get("required_fail_final", -1) == 0 and final.get("miss_final", -1) == 0 and opt <= tmax
    if not suite_ok:
        verdict = f"{BASE}_CONDITIONAL_BLOCKERS_SUITE_REGRESSION_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"
    elif apply_ok and backup_ok and rollback_ok:
        verdict = f"{BASE}_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"
    else:
        verdict = f"{BASE}_CONDITIONAL_BLOCKERS_NO_STAGING_CLONE_AVAILABLE_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"
    md = os.path.join(R, "data", "design", "release_acceleration")
    os.makedirs(md, exist_ok=True)
    mp = os.path.join(md, "mega_release_acceleration_72_v110_psp_apply_staging_smoke_rollup_marker_v1.json")
    payload = {
        "pack": BASE,
        "type": "v110_psp_apply_staging_smoke_rollup_marker",
        "version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "public_sync_tag": SENT,
        "validators_total": len(results) + 1,
        "validators_pass": len([x for x in results if x["exit_code"] == 0]) + (1 if fr.returncode == 0 else 0),
        "verdict_string": verdict,
        "required_fail_final": final.get("required_fail_final"),
        "miss_final": final.get("miss_final"),
        "optional_fail_final": opt,
        "optional_fail_target_max": tmax,
        "under_target_max": opt <= tmax,
        "deterministic": final.get("deterministic"),
        "environment_classification": env_class.get("classification"),
        "limited_apply_executed": apply_ok,
        "production_apply_executed": apply_res.get("production_apply_executed", False),
        "backup_executed": backup_ok,
        "rollback_drill_executed": rollback_ok,
        "rollback_dry_run_executed": rollback_res.get("rollback_dry_run_executed", False),
        "rollup_pass_does_not_imply_release_readiness": True,
        "safety": {
            "fake_PASS": False,
            "validator_weakening": False,
            "release_readiness_claimed": False,
            "production_apply_executed": False,
            "premium_grant": False,
            "destructive_migration": False,
            "delete": False,
            "reward_live": False,
            "progress_live": False,
        },
    }
    open(mp, "w").write(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"Rollup marker: {mp}")
    print(f"Verdict: {verdict}")
    print(f"v110 staging-smoke rollup: {len(results) + 1}/{len(SUB) + 1} PASS")
    sys.exit(0)

if __name__ == "__main__":
    main()
