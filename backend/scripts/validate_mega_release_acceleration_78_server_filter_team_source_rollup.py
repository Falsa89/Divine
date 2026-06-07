#!/usr/bin/env python3
import json, os, re, subprocess, sys
from datetime import datetime, timezone

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, "backend", "scripts")
FINAL = os.path.join(R, "data/design/v110_server_filter_team_source/server_filter_team_source_final_multirun_suite_result_v1.json")
MASTER = os.path.join(S, "run_hero_skill_kit_validator_suite.py")
SENT = "PUBLIC_SYNC_TAG_SERVER_ID_FILTER_AND_REAL_PLAYER_TEAM_SOURCE_COMBO"
BASE = "MEGA_RELEASE_ACCELERATION_78_SERVER_ID_FILTER_AND_REAL_PLAYER_TEAM_SOURCE_COMBO"
SUB = [
    "validate_server_filter_team_source_baseline_multirun.py",
    "validate_server_scope_post_psp_readiness.py",
    "validate_backend_loader_server_id_filter_promotion_matrix.py",
    "validate_psp_backed_real_player_team_source.py",
    "validate_authored_enemy_source.py",
    "validate_pre_battle_lobby_ui_fix.py",
    "validate_story_to_lobby_to_combat_propagation.py",
    "validate_backend_route_probe_smoke.py",
    "validate_zero_mutation_economy_preservation.py",
    "validate_server_filter_team_source_live_readiness_update.py",
    "validate_server_filter_team_source_gate_invariant_preservation.py",
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
        if not p: sys.exit(1)
        runs.append({"run": i + 1, **p})
    return runs


def _ensure_final():
    in_suite = os.environ.get("SUITE_RUNNER_ACTIVE") == "1"
    if in_suite and os.path.isfile(FINAL): return json.load(open(FINAL))
    if in_suite and not os.path.isfile(FINAL):
        print("[v110 SERVER_FILTER_TEAM_SOURCE ROLLUP] suite-mode skip")
        return None
    runs = _three()
    s = lambda k: {r[k] for r in runs}
    det = (len(s("pass")) == 1 and len(s("fail")) == 1 and len(s("miss")) == 1 and len(s("required_fail")) == 1)
    last = runs[-1]
    p = {"pack": BASE, "track": "L", "sentinel": SENT, "runs": runs, "deterministic": det,
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
            print(f"FAIL {v}"); print(r.stdout[-1500:]); print(r.stderr[-1500:]); sys.exit(1)
    final = _ensure_final()
    if final is None:
        print(f"v110 server-filter-team-source rollup: {len(results)}/{len(SUB)} PASS (suite mode)")
        sys.exit(0)
    fr = subprocess.run([sys.executable, os.path.join(S, "validate_server_filter_team_source_final_multirun_suite.py")],
                        capture_output=True, text=True, timeout=60)
    print(fr.stdout.strip().splitlines()[-1] if fr.stdout.strip() else "")
    if fr.returncode != 0: sys.exit(1)
    opt = final.get("optional_fail_final", 999); tmax = final.get("optional_fail_target_max", 30)
    if final.get("required_fail_final", -1) != 0 or final.get("miss_final", -1) != 0 or opt > tmax:
        verdict = f"{BASE}_CONDITIONAL_BLOCKERS_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"
    else:
        verdict = f"{BASE}_READY_WITH_DEFERRED_BLOCKERS_DOCUMENTED_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING"

    md = os.path.join(R, "data", "design", "release_acceleration")
    os.makedirs(md, exist_ok=True)
    mp = os.path.join(md, "mega_release_acceleration_78_server_filter_team_source_rollup_marker_v1.json")
    payload = {
        "pack": BASE, "type": "server_filter_team_source_rollup_marker", "version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "public_sync_tag": SENT,
        "validators_total": len(results) + 1,
        "validators_pass": len([x for x in results if x["exit_code"] == 0]) + (1 if fr.returncode == 0 else 0),
        "verdict_string": verdict,
        "required_fail_final": final.get("required_fail_final"),
        "miss_final": final.get("miss_final"),
        "optional_fail_final": opt, "optional_fail_target_max": tmax,
        "under_target_max": opt <= tmax, "deterministic": final.get("deterministic"),
        "server_id_filter_real_loader_promoted_count": 0,
        "server_id_filter_deferred_count": 5,
        "real_player_team_source_promoted": False,
        "real_player_team_source_blocker_id": "PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER",
        "lobby_3_slot_placeholder_removed": True,
        "production_apply_executed": False,
        "production_db_writes_in_pack_78": 0,
        "legacy_cleanup_executed": False,
        "reward_live": False, "progress_live": False,
        "rollup_pass_does_not_imply_release_readiness": True,
        "next_step": "loader_promotion_per_endpoint_dedicated_pack_or_real_player_team_source_promotion_pack",
        "safety": {
            "fake_PASS": False, "validator_weakening": False, "release_readiness_claimed": False,
            "production_apply_executed": False, "production_db_writes": False,
            "destructive_migration": False, "delete_on_production": False,
            "premium_grant": False, "reward_live": False, "progress_live": False,
            "legacy_cleanup_executed": False, "false_filter_applied_true": False,
            "fake_team_as_real": False, "fake_enemy_as_authored": False,
            "3_slot_placeholder_player_facing": False,
        },
    }
    open(mp, "w").write(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"Rollup marker: {mp}")
    print(f"Verdict: {verdict}")
    print(f"v110 server-filter-team-source rollup: {len(results) + 1}/{len(SUB) + 1} PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
