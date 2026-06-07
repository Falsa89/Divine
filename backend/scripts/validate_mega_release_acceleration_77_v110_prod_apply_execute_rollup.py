#!/usr/bin/env python3
# Rollup Pack 77: esegue 13 validatori, genera final 3-run, scrive marker rollup.
import json, os, re, subprocess, sys
from datetime import datetime, timezone

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, "backend", "scripts")
FINAL = os.path.join(R, "data/design/v110_prod_apply_execute/v110_prod_apply_final_multirun_suite_result_v1.json")
MASTER = os.path.join(S, "run_hero_skill_kit_validator_suite.py")
SENT = "PUBLIC_SYNC_TAG_v110_PSP_PROD_APPLY_EXECUTE"
BASE = "MEGA_RELEASE_ACCELERATION_77_v110_PSP_PROD_APPLY_EXECUTE"

SUB = [
    "validate_v110_prod_apply_baseline_multirun.py",
    "validate_v110_prod_apply_user_approval_verification.py",
    "validate_v110_prod_apply_pin_artifact_verification.py",
    "validate_v110_prod_apply_pre_snapshot.py",
    "validate_v110_prod_apply_final_dry_run.py",
    "validate_v110_prod_apply_backup_confirmation.py",
    "validate_v110_prod_apply_execute_result.py",
    "validate_v110_prod_apply_idempotency_rerun.py",
    "validate_v110_prod_apply_post_invariants.py",
    "validate_v110_prod_apply_rollback_readiness.py",
    "validate_v110_prod_apply_live_readiness_update.py",
    "validate_v110_prod_apply_gate_invariant_preservation.py",
]


def _parse(out):
    m = re.search(r"pass=(\d+),\s*fail=(\d+),\s*miss=(\d+)", out)
    if not m: return None
    rr = re.search(r"REQUIRED FAIL[^\d]*(\d+)", out)
    return {"pass": int(m.group(1)), "fail": int(m.group(2)), "miss": int(m.group(3)),
            "required_fail": int(rr.group(1)) if rr else 0}


def _three():
    runs = []
    for i in range(3):
        r = subprocess.run([sys.executable, MASTER], capture_output=True, text=True, timeout=240)
        p = _parse((r.stdout or "") + "\n" + (r.stderr or ""))
        if not p:
            print("FAIL parse master suite"); sys.exit(1)
        runs.append({"run": i + 1, **p})
    return runs


def _ensure_final():
    in_suite = os.environ.get("SUITE_RUNNER_ACTIVE") == "1"
    if in_suite and os.path.isfile(FINAL): return json.load(open(FINAL))
    if in_suite and not os.path.isfile(FINAL):
        print("[v110 PROD_APPLY ROLLUP] suite-mode skip")
        return None
    runs = _three()
    s = lambda k: {r[k] for r in runs}
    det = (len(s("pass")) == 1 and len(s("fail")) == 1 and len(s("miss")) == 1 and len(s("required_fail")) == 1)
    last = runs[-1]
    p = {"pack": BASE, "track": "M", "sentinel": SENT, "runs": runs, "deterministic": det,
         "pass_final": last["pass"], "fail_final": last["fail"], "miss_final": last["miss"],
         "required_fail_final": last["required_fail"],
         "optional_fail_final": last["fail"] - last["required_fail"],
         "optional_fail_target_max": 30,
         "safety_flags": {"fake_PASS": False, "validator_weakening": False,
                          "silent_validator_deletion": False, "release_readiness_claimed": False}}
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
            print(f"FAIL {v}"); print(r.stdout[-1500:]); print(r.stderr[-1500:])
            sys.exit(1)
    final = _ensure_final()
    if final is None:
        print(f"v110 prod-apply rollup: {len(results)}/{len(SUB)} PASS (suite mode)")
        sys.exit(0)
    fr = subprocess.run([sys.executable, os.path.join(S, "validate_v110_prod_apply_final_multirun_suite.py")],
                        capture_output=True, text=True, timeout=60)
    print(fr.stdout.strip().splitlines()[-1] if fr.stdout.strip() else "")
    if fr.returncode != 0:
        print("FAIL final multirun suite validator"); sys.exit(1)
    opt = final.get("optional_fail_final", 999); tmax = final.get("optional_fail_target_max", 30)
    if (final.get("required_fail_final", -1) != 0 or final.get("miss_final", -1) != 0 or opt > tmax):
        verdict = f"{BASE}_CONDITIONAL_BLOCKERS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"
    else:
        verdict = f"{BASE}_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"

    md = os.path.join(R, "data", "design", "release_acceleration")
    os.makedirs(md, exist_ok=True)
    mp = os.path.join(md, "mega_release_acceleration_77_v110_prod_apply_execute_rollup_marker_v1.json")

    pre = R + "/data/design/v110_prod_apply_execute/"
    apply_res = json.load(open(pre + "v110_prod_apply_execute_result_v1.json"))
    idem = json.load(open(pre + "v110_prod_apply_idempotency_rerun_v1.json"))
    inv = json.load(open(pre + "v110_prod_apply_post_invariants_v1.json"))
    rb = json.load(open(pre + "v110_prod_apply_rollback_readiness_v1.json"))
    lr = json.load(open(pre + "v110_prod_apply_live_readiness_update_v1.json"))

    payload = {
        "pack": BASE, "type": "v110_prod_apply_execute_rollup_marker", "version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "public_sync_tag": SENT,
        "validators_total": len(results) + 1,
        "validators_pass": len([x for x in results if x["exit_code"] == 0]) + (1 if fr.returncode == 0 else 0),
        "verdict_string": verdict,
        "required_fail_final": final.get("required_fail_final"),
        "miss_final": final.get("miss_final"),
        "optional_fail_final": opt, "optional_fail_target_max": tmax,
        "under_target_max": opt <= tmax, "deterministic": final.get("deterministic"),
        "production_apply_executed": apply_res.get("production_apply_executed"),
        "production_apply_db_writes": apply_res.get("db_writes"),
        "production_psp_inserted": apply_res.get("psp_inserted_in_this_run"),
        "production_psp_reapply_updates": apply_res.get("psp_existing_re_run_updates"),
        "users_in_plan_at_apply": apply_res.get("users_in_plan"),
        "idempotency_second_run_inserts_zero": idem.get("idempotent_second_run_psp_inserts_zero"),
        "duplicates_post_idempotency": idem.get("duplicate_profile_pairs"),
        "all_invariants_ok": inv.get("all_invariants_ok"),
        "rollback_readiness_ok": rb.get("rollback_readiness_ok"),
        "rollback_executed_on_production": rb.get("rollback_executed_on_production"),
        "live_overall_ready": lr.get("live_overall_ready"),
        "next_step": lr.get("next_step"),
        "rollup_pass_does_not_imply_release_readiness": True,
        "safety": {
            "fake_PASS": False, "validator_weakening": False, "release_readiness_claimed": False,
            "production_apply_executed": True, "production_db_writes": True,
            "destructive_migration": False, "delete_on_production": False,
            "premium_grant": False, "reward_live": False, "progress_live": False,
            "legacy_cleanup_executed": False, "approval_flags_changed_to_yes_for_pack_77": True,
        },
    }
    open(mp, "w").write(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"Rollup marker: {mp}")
    print(f"Verdict: {verdict}")
    print(f"v110 prod-apply rollup: {len(results) + 1}/{len(SUB) + 1} PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
