#!/usr/bin/env python3
"""v108_POSTQA_D - Track E authoritative preflight contract validator."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "postqa", "v108_postqa_d_authoritative_preflight_contract_v1.json")
d = json.load(open(P))
assert d.get("sentinel") == "PUBLIC_SYNC_TAG_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS"
ff = d.get("feature_flags", {})
required = [
    "BATTLE_LAUNCH_AUTHORITATIVE_ENABLED",
    "REWARD_LIVE_ENABLED",
    "PROGRESS_LIVE_ENABLED",
    "SERVER_SCOPED_RUNTIME_ENABLED",
    "AUTHORITATIVE_BATTLE_ENGINE_ENABLED",
]
for k in required:
    assert k in ff and ff[k] is False, f"feature flag {k} must be present and false"
out = d.get("out_of_scope_in_pack_d", [])
for must in (
    "battle_engine_formula_rewrite",
    "authoritative_live_claim",
    "backend_isolation_live_claim",
    "production_db_writes",
    "reward_grant",
    "progress_live_write",
):
    assert must in out, f"out_of_scope must include {must}"
sf = d.get("safety_flags", {})
assert sf.get("authoritative_live_claim") is False
assert sf.get("flag_enabled_by_default") is False
print("[v108_POSTQA_D AUTHORITATIVE_PREFLIGHT] OK flags_off=5 out_of_scope_documented")
sys.exit(0)
