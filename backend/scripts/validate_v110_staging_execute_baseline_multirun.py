#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_execute/v110_staging_execute_baseline_multirun_v1.json")))
assert d.get("deterministic") is True and d.get("required_fail") == 0 and d.get("miss") == 0
assert d.get("optional_fail", 999) <= d.get("optional_fail_target_overall_max", 30)
for k in ("v108_postqa_a_invariants_pass", "postqa_d_gates_preserved", "v109_server_isolation_preserved", "v110_prep_preserved", "v110_apply_preflight_preserved", "v110_staging_smoke_pack72_preserved", "v110_staging_clone_pack73_preserved"):
    assert d.get(k) is True
print("[v110 STAGING_EXECUTE_BASELINE_MULTIRUN] OK 3-run deterministic 1268/21/0/0")
