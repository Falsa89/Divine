#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(R, "data/design/v110_psp_migration/v110_final_multirun_suite_result_v1.json")
assert os.path.isfile(P), "final multirun not generated yet"
d = json.load(open(P))
assert d.get("deterministic") is True
assert d.get("required_fail_final") == 0 and d.get("miss_final") == 0
opt = d.get("optional_fail_final", 999)
tmax = d.get("optional_fail_target_max", 30)
assert opt <= tmax, f"optional {opt} > tmax {tmax}"
print(f"[v110 FINAL_MULTIRUN] OK required=0 miss=0 optional={opt} target_max={tmax}")
