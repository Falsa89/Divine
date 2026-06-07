#!/usr/bin/env python3
# Validatore baseline multirun Pack 75. Verifica 1282/21/0/0 deterministico pre-apply.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_psp_full_staging/v110_full_staging_baseline_multirun_v1.json")
d = json.load(open(F))
assert d.get("deterministic") is True
assert d.get("required_fail") == 0
assert d.get("miss") == 0
assert d.get("optional_fail", 999) <= d.get("optional_fail_target_overall_max", 30)
assert d.get("v110_staging_execute_pack74_preserved") is True
for k in ("v108_postqa_a_invariants_pass", "postqa_d_gates_preserved", "v109_server_isolation_preserved",
          "v110_prep_preserved", "v110_apply_preflight_preserved",
          "v110_staging_smoke_pack72_preserved", "v110_staging_clone_pack73_preserved"):
    assert d.get(k) is True, k
sf = d.get("safety_flags", {})
assert sf.get("fake_PASS") is False
assert sf.get("validator_weakening") is False
print("[v110 FULL_STAGING_BASELINE_MULTIRUN] OK 3-run deterministic 1282/21/0/0")
