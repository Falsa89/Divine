#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_server_filter_team_source/story_to_lobby_to_combat_propagation_v1.json")
d = json.load(open(F))
for k in ("story_passes_encounter_id_to_lobby", "story_passes_enemy_source_to_lobby",
          "lobby_passes_launch_context_to_combat", "lobby_passes_battle_launch_id_to_combat",
          "lobby_passes_server_id_to_combat", "launch_context_includes_server_id",
          "launch_context_includes_encounter_id"):
    assert d.get(k) is True, k
assert d.get("propagation_chain_intact") is True
sf = d.get("safety_flags", {})
assert sf.get("fake_PASS") is False
print("[v110 STORY_TO_LOBBY_TO_COMBAT_PROPAGATION] OK chain intact")
