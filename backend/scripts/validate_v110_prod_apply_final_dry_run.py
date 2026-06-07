#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_apply_execute/v110_prod_apply_final_dry_run_v1.json")
d = json.load(open(F))
assert d.get("cmd_returncode") == 0
assert d.get("dry_run_script_status") == "PLAN_ONLY_NO_WRITE"
assert d.get("dry_run_apply_executed") is False
assert d.get("dry_run_db_writes") == 0
assert d.get("safe") is True
assert d.get("authorization_string_match_in_script") is True
assert d.get("pinned_commit_match_in_script") is True
sf = d.get("safety_flags", {})
for k in ("production_apply", "production_db_writes", "fake_PASS"):
    assert sf.get(k) is False, k
print("[v110 PROD_APPLY_FINAL_DRY_RUN] OK rc=0 PLAN_ONLY_NO_WRITE writes=0")
