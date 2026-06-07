#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_server_filter_team_source/server_filter_team_source_baseline_multirun_v1.json")
d = json.load(open(F))
assert d.get("deterministic") is True
assert d.get("required_fail") == 0 and d.get("miss") == 0
assert d.get("optional_fail", 999) <= d.get("optional_fail_target_overall_max", 30)
assert d.get("v110_prod_apply_pack77_preserved") is True
sf = d.get("safety_flags", {})
assert sf.get("fake_PASS") is False and sf.get("validator_weakening") is False
print("[v110 SERVER_FILTER_TEAM_SOURCE_BASELINE_MULTIRUN] OK 1324/21/0/0")
