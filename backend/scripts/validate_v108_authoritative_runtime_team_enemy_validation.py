#!/usr/bin/env python3
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "authoritative_runtime", "v108_authoritative_runtime_team_enemy_validation_v1.json")
d = json.load(open(P))
ptr = d.get("player_team_rules", {})
assert ptr.get("staging_min_size", 0) >= 1
assert ptr.get("staging_max_size", 0) == 6
assert ptr.get("full_6_required_for_live") is True
fb = set(ptr.get("forbidden_markers", []))
for m in ("PLAYER_SAFE_FALLBACK_TEAM","FAKE_TEAM","MOCK_TEAM","FALLBACK_TEAM"):
    assert m in fb, f"player forbidden marker missing: {m}"
assert ptr.get("block_code") == "BATTLE_RESULT_PLAYER_TEAM_REQUIRED"
etr = d.get("enemy_team_rules", {})
for m in ("GENERATED_ENEMY_RANDOM","PLACEHOLDER_ENEMY","ALPHA_ENEMY","STUB_ENEMY"):
    assert m in set(etr.get("forbidden_markers_unless_qa", [])), f"enemy marker missing: {m}"
assert etr.get("block_code") == "BATTLE_RESULT_ENEMY_TEAM_REQUIRED"
rsp = d.get("router_static_proof", {})
assert rsp.get("contains_all_player_forbidden_markers") is True
assert rsp.get("contains_all_enemy_forbidden_markers") is True
assert rsp.get("rejects_authoritative_live_true") is True
# verify router really contains markers
RT = os.path.join(ROOT, "backend", "routes", "v108_authoritative_runtime_resolve.py")
txt = open(RT).read()
for m in ("PLAYER_SAFE_FALLBACK_TEAM","FAKE_TEAM","MOCK_TEAM","FALLBACK_TEAM","GENERATED_ENEMY_RANDOM","PLACEHOLDER_ENEMY","ALPHA_ENEMY"):
    assert m in txt, f"router missing marker {m}"
print("[v108_AUTHORITATIVE_RUNTIME TEAM_ENEMY_VALIDATION] OK player_markers>=4 enemy_markers>=4 full_6_required_for_live=true")
sys.exit(0)
