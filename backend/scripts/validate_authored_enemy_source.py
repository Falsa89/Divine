#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_server_filter_team_source/authored_enemy_source_v1.json")
d = json.load(open(F))
assert d.get("enemy_source_kind") == "authored_catalog_inline_mirror"
assert d.get("lobby_enemy_catalog_present") is True
assert d.get("enemy_is_random_runtime") is False
assert d.get("enemy_fallback_random_allowed") is False
assert d.get("enemy_runtime_generated") is False
assert d.get("lobby_blocker_when_no_authored_encounter") == "AUTHORED_ENCOUNTER_SOURCE_PENDING"
assert d.get("lobby_disables_battle_launch_when_blocker_active") is True
sf = d.get("safety_flags", {})
assert sf.get("fake_enemy_as_authored") is False
assert sf.get("fake_PASS") is False
print("[v110 AUTHORED_ENEMY_SOURCE] OK authored catalog enforced")
