#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_apply_execute/v110_prod_apply_user_approval_verification_v1.json")
d = json.load(open(F))
assert d.get("approval_string_match") is True
assert d.get("approval_string_received_length") == len("AUTORIZZO_V110_PSP_PROD_APPLY_EXECUTE_SU_DIVINE_WAIFUS")
assert d.get("pinned_commit_match") is True
assert d.get("pinned_commit_expected") == "fc13fa32ef91530eca031fbeec283bea66bb21d9"
assert d.get("pinned_commit_received") == "fc13fa32ef91530eca031fbeec283bea66bb21d9"
assert d.get("all_5_v110_flags_yes_in_env") is True
sf = d.get("safety_flags", {})
assert sf.get("fake_PASS") is False
assert sf.get("release_readiness_claimed") is False
print("[v110 PROD_APPLY_USER_APPROVAL_VERIFICATION] OK auth string + pin + flags verified")
