#!/usr/bin/env python3
"""v108_AUTHORITATIVE_PRE - Track E real team source contract."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "authoritative_pre", "v108_authoritative_pre_real_team_source_contract_v1.json")
d = json.load(open(P))
assert d.get("block_code_when_team_not_safe") == "REAL_PLAYER_TEAM_SOURCE_PENDING"
assert d.get("battle_instance_endpoint_rejects_fake_team") is True
assert d.get("6_slot_formation_exists") is True
fb = set(d.get("forbidden_markers", []))
assert "PLAYER_SAFE_FALLBACK_TEAM" in fb
# verify router rejects PLAYER_SAFE_FALLBACK_TEAM (static check)
RT = os.path.join(ROOT, "backend", "routes", "v108_authoritative_pre_instance.py")
rt_txt = open(RT).read()
assert "PLAYER_SAFE_FALLBACK_TEAM" in rt_txt
assert d.get("safety_flags", {}).get("fake_team_as_real") is False
print("[v108_AUTHORITATIVE_PRE REAL_TEAM_SOURCE] OK forbidden_markers>=5 router_rejects_fake_team")
sys.exit(0)
