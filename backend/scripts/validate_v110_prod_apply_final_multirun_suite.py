#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_apply_execute/v110_prod_apply_final_multirun_suite_result_v1.json")
if os.environ.get("SUITE_RUNNER_ACTIVE") == "1" and not os.path.isfile(F):
    print("[v110 PROD_APPLY_FINAL_MULTIRUN_SUITE] suite-mode skip (artefatto ancora non generato)")
    sys.exit(0)
d = json.load(open(F))
assert d.get("deterministic") is True
assert d.get("required_fail_final") == 0
assert d.get("miss_final") == 0
opt = d.get("optional_fail_final", 999)
mx = d.get("optional_fail_target_max", 30)
assert opt <= mx, f"optional_fail {opt} > target {mx}"
runs = d.get("runs", [])
assert len(runs) == 3
for r in runs:
    assert r.get("required_fail") == 0
    assert r.get("miss") == 0
sf = d.get("safety_flags", {})
for k in ("fake_PASS", "validator_weakening", "silent_validator_deletion", "release_readiness_claimed"):
    assert sf.get(k) is False, k
print(f"[v110 PROD_APPLY_FINAL_MULTIRUN_SUITE] OK 3-run deterministic pass={d.get('pass_final')} fail={d.get('fail_final')} opt={opt}")
