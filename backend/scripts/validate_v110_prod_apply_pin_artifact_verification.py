#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_apply_execute/v110_prod_apply_pin_artifact_verification_v1.json")
d = json.load(open(F))
assert d.get("exact_git_commit_pin_value") == "fc13fa32ef91530eca031fbeec283bea66bb21d9"
assert d.get("exact_git_commit_pin_match") is True
assert d.get("all_pins_present") is True
assert d.get("backup_artifact_pin_value")
assert d.get("dry_run_hash_pin_value")
assert d.get("rollback_plan_hash_pin_value")
sf = d.get("safety_flags", {})
assert sf.get("fake_PASS") is False
assert sf.get("validator_weakening") is False
print("[v110 PROD_APPLY_PIN_ARTIFACT_VERIFICATION] OK all pins matched")
