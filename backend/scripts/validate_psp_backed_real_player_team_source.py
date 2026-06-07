#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_server_filter_team_source/psp_backed_real_player_team_source_v1.json")
d = json.load(open(F))
assert d.get("team_endpoint") == "/api/team/get-formation"
assert d.get("endpoint_filters_by_server_id_currently") is False
assert d.get("real_player_team_source_promoted_in_pack_78") is False
assert d.get("fake_player_team_built_in_pack_78") is False
assert d.get("lobby_blocker_when_no_real_team") == "PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER"
assert d.get("lobby_disables_battle_launch_when_blocker_active") is True
assert d.get("no_3_slot_placeholder_player_facing") is True
assert d.get("no_hardcoded_s1_silent_fallback") is True
sf = d.get("safety_flags", {})
for k in ("fake_team_as_real", "3_slot_placeholder_player_facing", "release_readiness_claimed", "fake_PASS"):
    assert sf.get(k) is False, k
print("[v110 PSP_BACKED_REAL_PLAYER_TEAM_SOURCE] OK blocker enforced, no fake team")
