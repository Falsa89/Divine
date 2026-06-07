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
# HOTFIX B2: exact_git_commit_pin DEVE essere popolato (non null) e di lunghezza 40 (git sha-1 hex).
egcp = pins["exact_git_commit_pin"]
assert egcp.get("pinned_value") is not None, "exact_git_commit_pin.pinned_value cannot be null"
assert isinstance(egcp["pinned_value"], str) and len(egcp["pinned_value"]) == 40, (
    f"exact_git_commit_pin.pinned_value must be a 40-char git sha, got len={len(egcp.get('pinned_value') or '')}"
)
assert all(ch in "0123456789abcdef" for ch in egcp["pinned_value"]), "pinned_value must be hex"
# Il pin DEVE riferire il commit hotfix B1 esattamente, non un commit successivo.
PACK_76_B1_COMMIT = "fc13fa32ef91530eca031fbeec283bea66bb21d9"
assert egcp["pinned_value"] == PACK_76_B1_COMMIT, (
    f"pinned_value must be the Pack 76 B1 hotfix commit {PACK_76_B1_COMMIT}, got {egcp['pinned_value']}"
)
assert egcp.get("pinned_at_utc"), "exact_git_commit_pin.pinned_at_utc must be set"
assert egcp.get("pin_source") == "hard_coded_at_pack_76_hotfix_b2"
assert egcp.get("pin_rationale"), "pin_rationale must explain why this commit was chosen"
hotfix_chain = egcp.get("hotfix_chain", [])
assert "v110_PROD_PREFLIGHT_B1_DRY_RUN_INVOCATION_AND_DIFF_RECONCILIATION" in hotfix_chain
assert "v110_PROD_PREFLIGHT_B2_APPROVAL_GATE_COMMIT_PIN_FIX" in hotfix_chain
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
