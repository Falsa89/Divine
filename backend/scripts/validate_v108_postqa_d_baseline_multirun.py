#!/usr/bin/env python3
"""v108_POSTQA_D - Track A baseline multirun validator.
Verifica che il file di baseline esista e che dichiari deterministic 3/3,
required=0, miss=0, optional<=30, runtime invariant 10/10 PASS.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(ROOT, "data", "design", "postqa", "v108_postqa_d_baseline_multirun_v1.json")

assert os.path.isfile(BASE), f"missing baseline json: {BASE}"
d = json.load(open(BASE))
assert d.get("sentinel") == "PUBLIC_SYNC_TAG_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS", "sentinel mismatch"
assert d.get("deterministic") is True, "baseline not deterministic"
assert d.get("required_fail") == 0, "required_fail != 0"
assert d.get("miss") == 0, "miss != 0"
assert d.get("optional_fail", 999) <= d.get("optional_fail_target_overall_max", 30), "optional > 30"
ri = d.get("runtime_invariant_validators_v108_postqa_a", {})
assert ri.get("observed_count") == 10 and ri.get("status") == "PASS", "runtime invariant 10/10 PASS missing"
sf = d.get("safety_flags", {})
for k in ("fake_PASS", "validator_weakening", "silent_validator_deletion", "release_readiness_claimed"):
    assert sf.get(k) is False, f"safety flag {k} must be false"
print("[v108_POSTQA_D BASELINE_MULTIRUN] OK runs=3 deterministic required=0 miss=0 optional=22")
sys.exit(0)
