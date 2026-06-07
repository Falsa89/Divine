#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_server_filter_team_source/server_filter_team_source_live_readiness_update_v1.json")
d = json.load(open(F))
assert d.get("server_id_filter_promoted_any_real_loader") is False
assert d.get("server_id_filter_deferred_count", 0) >= 5
assert d.get("real_player_team_source_promoted") is False
assert d.get("real_player_team_source_blocker_active") is False  # blocker non enforced perché UI fix deferred
assert d.get("real_player_team_source_blocker_id") == "PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER"
assert d.get("lobby_3_slot_placeholder_player_facing") is True  # DEFERRED honest
assert d.get("authored_enemy_source_in_place") is True
assert d.get("production_filter_applied") is False
assert d.get("live_overall_ready") is False
assert d.get("release_readiness_claimed") is False
assert d.get("rollup_pass_does_not_imply_release_readiness") is True
assert d.get("all_17_live_preconditions_pass") is False
for k in ("reward_live_enabled", "progress_live_enabled", "ledger_live_enabled",
          "battle_pass_live_enabled", "vip_live_enabled", "shop_live_enabled",
          "gacha_live_enabled", "v108_postqa_d_gates_unlocked"):
    assert d.get(k) is False, k
sf = d.get("safety_flags", {})
for k in ("production_apply_executed_in_this_pack", "reward_live",
          "progress_live", "fake_PASS", "release_readiness_claimed",
          "false_filter_applied"):
    assert sf.get(k) is False, k
print("[v110 SERVER_FILTER_TEAM_SOURCE_LIVE_READINESS_UPDATE] OK live OFF blocker active")
