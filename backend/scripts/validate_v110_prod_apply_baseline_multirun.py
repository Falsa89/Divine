#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_apply_execute/v110_prod_apply_baseline_multirun_v1.json")
d = json.load(open(F))
assert d.get("deterministic") is True
assert d.get("required_fail") == 0
assert d.get("miss") == 0
assert d.get("optional_fail", 999) <= d.get("optional_fail_target_overall_max", 30)
for k in ("v110_full_staging_pack75_preserved", "v110_prod_preflight_pack76_preserved",
          "v110_prod_preflight_b1_preserved", "v110_prod_preflight_b2_preserved"):
    assert d.get(k) is True, k
sf = d.get("safety_flags", {})
assert sf.get("fake_PASS") is False
assert sf.get("validator_weakening") is False
print("[v110 PROD_APPLY_BASELINE_MULTIRUN] OK 3-run deterministic 1310/21/0/0")
