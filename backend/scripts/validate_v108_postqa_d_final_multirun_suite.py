#!/usr/bin/env python3
"""v108_POSTQA_D - Track H final multirun suite validator.
Legge il file di esito del final 3-run generato dal rollup e verifica:
- required=0, miss=0, optional<=30, deterministic 3/3.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "postqa", "v108_postqa_d_final_multirun_suite_result_v1.json")
assert os.path.isfile(P), "final multirun result not generated yet; run rollup first"
d = json.load(open(P))
assert d.get("sentinel") == "PUBLIC_SYNC_TAG_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS"
assert d.get("deterministic") is True
assert d.get("required_fail_final") == 0
assert d.get("miss_final") == 0
opt = d.get("optional_fail_final", 999)
tmax = d.get("optional_fail_target_max", 30)
assert opt <= tmax, f"optional fail {opt} > target_max {tmax}"
sf = d.get("safety_flags", {})
for k in ("fake_PASS", "validator_weakening", "silent_validator_deletion", "release_readiness_claimed"):
    assert sf.get(k) is False, f"safety flag {k} must be false"
print(f"[v108_POSTQA_D FINAL_MULTIRUN] OK required=0 miss=0 optional={opt} target_max={tmax}")
sys.exit(0)
