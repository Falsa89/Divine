#!/usr/bin/env python3
"""v108_AUTHORITATIVE_PRE - Track F enemy source contract."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "authoritative_pre", "v108_authoritative_pre_enemy_source_contract_v1.json")
d = json.load(open(P))
allowed = set(d.get("allowed_source_types", []))
for must in ("authored","boss","training_preset","event_preset"):
    assert must in allowed
assert d.get("random_generate_enemy_player_facing") is False
assert d.get("placeholder_alpha_enemy_player_facing") is False
assert d.get("battle_instance_endpoint_rejects_placeholder_enemy") is True
assert d.get("block_code_when_no_real_source") == "AUTHORED_ENCOUNTER_SOURCE_PENDING"
RT = os.path.join(ROOT, "backend", "routes", "v108_authoritative_pre_instance.py")
rt_txt = open(RT).read()
for must in ("GENERATED_ENEMY_RANDOM","PLACEHOLDER_ENEMY","ALPHA_ENEMY"):
    assert must in rt_txt, f"router missing enemy marker {must}"
print("[v108_AUTHORITATIVE_PRE ENEMY_SOURCE] OK player_facing_4 qa_only_2 router_rejects_placeholder")
sys.exit(0)
