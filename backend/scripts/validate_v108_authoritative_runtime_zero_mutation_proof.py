#!/usr/bin/env python3
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "authoritative_runtime", "v108_authoritative_runtime_zero_mutation_proof_v1.json")
d = json.load(open(P))
sp = d.get("static_proof", {})
assert sp.get("db_imports") == []
assert sp.get("motor_imports") == []
assert sp.get("battle_engine_imports") == []
assert sp.get("battle_simulate_calls") == []
assert sp.get("legacy_mutating_endpoint_calls") == []
assert sp.get("reward_assignment_statements") == []
rp = d.get("runtime_proof", {})
assert rp.get("db_writes_observed") == 0
assert rp.get("reward_grants_observed") == 0
assert rp.get("progress_writes_observed") == 0
assert rp.get("currency_mutations_observed") == 0
assert rp.get("inventory_mutations_observed") == 0
assert rp.get("user_heroes_exp_mutations_observed") == 0
# verify router file really has no DB / no simulate / no battle_engine import
RT = os.path.join(ROOT, "backend", "routes", "v108_authoritative_runtime_resolve.py")
txt = open(RT).read()
for forbidden in ("motor","AsyncIOMotorClient","await db"," db.","from battle_engine","import battle_engine","/api/battle/simulate","battle/simulate"):
    assert forbidden not in txt, f"static proof violated: {forbidden!r} present"
print("[v108_AUTHORITATIVE_RUNTIME ZERO_MUTATION_PROOF] OK static+runtime db=0 reward=0 progress=0")
sys.exit(0)
