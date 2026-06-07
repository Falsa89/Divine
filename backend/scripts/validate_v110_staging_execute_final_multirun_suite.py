#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(R, "data/design/v110_psp_apply_staging_execute/v110_staging_execute_final_multirun_suite_result_v1.json")
assert os.path.isfile(P)
d = json.load(open(P))
assert d.get("deterministic") is True
assert d.get("required_fail_final") == 0 and d.get("miss_final") == 0
opt = d.get("optional_fail_final", 999); tmax = d.get("optional_fail_target_max", 30)
assert opt <= tmax
print(f"[v110 STAGING_EXECUTE_FINAL_MULTIRUN] OK required=0 miss=0 optional={opt} target_max={tmax}")
