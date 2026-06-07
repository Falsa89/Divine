#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_server_filter_team_source/server_filter_team_source_gate_invariant_preservation_v1.json")
d = json.load(open(F))
for k in ("battle_engine_formula_modified", "battle_simulate_route_invoked_from_staging",
          "battle_simulate_route_invoked_from_live", "validators_weakened",
          "validators_silently_deleted", "fake_PASS_introduced",
          "approval_flags_changed_to_yes_for_pack_78"):
    assert d.get(k) is False, k
for k in ("postqa_d_gates_preserved", "server_isolation_v109_preserved",
          "v110_prep_preserved", "v110_apply_preflight_preserved",
          "v110_staging_smoke_pack72_preserved", "v110_staging_clone_pack73_preserved",
          "v110_staging_execute_pack74_preserved", "v110_full_staging_pack75_preserved",
          "v110_prod_preflight_pack76_preserved", "v110_prod_preflight_b1_preserved",
          "v110_prod_preflight_b2_preserved", "v110_prod_apply_pack77_preserved"):
    assert d.get(k) is True, k
ff = d.get("feature_flags_live_state", {})
for k in ("reward_live", "progress_live", "ledger_live", "battlepass_live",
          "vip_live", "shop_live", "gacha_live"):
    assert ff.get(k) is False, k
assert d.get("production_db_writes_total_in_pack_78") == 0
sf = d.get("safety_flags", {})
for k in ("battle_engine_formula_rewrite", "validator_weakening", "fake_PASS",
          "release_readiness_claimed", "postqa_d_unlocked",
          "approval_flags_changed_to_yes"):
    assert sf.get(k) is False, k
print("[v110 SERVER_FILTER_TEAM_SOURCE_GATE_INVARIANT_PRESERVATION] OK preserved")
