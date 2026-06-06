#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_preflight/v110_staging_apply_smoke_plan_v1.json")))
assert d.get("environment") == "staging"
assert d.get("production_db_forbidden_in_smoke") is True
steps = d.get("steps", [])
assert len(steps) >= 10, f"smoke plan must have >=10 steps, got {len(steps)}"
for must in ("step_01_mongodump_backup_staging", "step_02_run_apply_with_dry_run_flag", "step_11_run_apply_idempotent_second_time_with_limit_5", "step_14_run_rollback_dry_run"):
    assert must in steps, f"smoke step missing {must}"
exp = d.get("expected_results", {})
assert exp.get("db_writes_in_dry_run") == 0
assert exp.get("db_writes_in_plan_only") == 0
assert exp.get("premium_balance_diff") == 0
assert exp.get("hard_balance_diff") == 0
assert exp.get("team_size_diff") == 0
assert exp.get("runtime_invariants_pass") is True
assert d.get("smoke_executed_in_this_pack") is False
assert d.get("db_writes_in_this_pack") == 0
for k in ("production_db_smoke", "fake_PASS", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 STAGING_APPLY_SMOKE_PLAN] OK steps={len(steps)} smoke_executed=false")
