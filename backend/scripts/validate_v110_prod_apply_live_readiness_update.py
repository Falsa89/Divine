#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_apply_execute/v110_prod_apply_live_readiness_update_v1.json")
d = json.load(open(F))
assert d.get("production_apply_executed") is True
assert d.get("production_apply_target") == "divine_waifus"
assert d.get("production_apply_server_id") == "s1"
assert d.get("production_apply_psp_inserted", 0) > 0
assert d.get("production_apply_idempotent") is True
assert d.get("production_filter_applied") is False
assert d.get("server_id_filter_applied") is False
assert d.get("real_player_team_source") is False
assert d.get("live_overall_ready") is False
assert d.get("release_readiness_claimed") is False
assert d.get("rollup_pass_does_not_imply_release_readiness") is True
assert d.get("all_17_live_preconditions_pass") is False
for k in ("reward_live_enabled", "progress_live_enabled", "ledger_live_enabled",
          "battle_pass_live_enabled", "vip_live_enabled", "shop_live_enabled",
          "gacha_live_enabled", "v108_postqa_d_gates_unlocked"):
    assert d.get(k) is False, k
ps = d.get("preconditions_status", {})
assert ps.get("psp_production_apply_green") is True
assert ps.get("psp_production_idempotent") is True
assert ps.get("psp_production_rollback_readiness") is True
for k in ("reward_live_precondition", "progress_live_precondition",
          "ledger_live_precondition", "server_id_filter_active",
          "real_player_team_source_active"):
    assert ps.get(k) is False, k
ns = (d.get("next_step", "") or "").lower()
assert "server_id_filter" in ns or "real_player_team_source" in ns
sf = d.get("safety_flags", {})
for k in ("reward_live", "progress_live", "fake_PASS", "release_readiness_claimed"):
    assert sf.get(k) is False, k
print("[v110 PROD_APPLY_LIVE_READINESS_UPDATE] OK production_apply done, live OFF, next=server_id_filter_combo")
