#!/usr/bin/env python3
# Pack 76 Track H: production approval gate matrix.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_preflight/v110_production_approval_gate_matrix_v1.json")
d = json.load(open(F))
assert d.get("production_execute_allowed") is False
assert d.get("missing_user_approval") is True
assert d.get("apply_not_executed") is True
flags = d.get("required_flags", {})
for flag in ("V110_PSP_APPLY", "V110_BACKUP_CONFIRMED",
             "V110_USER_EXPLICIT_DB_WRITE_APPROVAL",
             "V110_ROLLBACK_PLAN_CONFIRMED",
             "V110_PRODUCTION_DB_EXPLICIT_APPROVAL"):
    fd = flags.get(flag, {})
    assert fd.get("required_value") == "YES", flag
    assert fd.get("satisfied") is False, flag
pins = d.get("required_artifact_pins", {})
for pin in ("exact_git_commit_pin", "backup_artifact_pin", "dry_run_hash_pin", "rollback_plan_hash_pin"):
    assert pin in pins, pin
assert pins["backup_artifact_pin"]["pinned_value"], "backup pin must be set"
assert pins["dry_run_hash_pin"]["pinned_value"], "dry-run pin must be set"
assert pins["rollback_plan_hash_pin"]["pinned_value"], "rollback pin must be set"
assert d.get("maintenance_window_required") is True
assert isinstance(d.get("maintenance_window_proposed_minimum_minutes"), int)
assert d.get("maintenance_window_proposed_minimum_minutes") >= 15
assert isinstance(d.get("emergency_stop_command"), str) and len(d["emergency_stop_command"]) > 0
sf = d.get("safety_flags", {})
for k in ("production_execute_allowed", "approval_flags_silently_set_to_yes",
          "fake_PASS", "release_readiness_claimed"):
    assert sf.get(k) is False, k
print("[v110 PROD_APPROVAL_GATE_MATRIX] OK production_execute_allowed=false")
