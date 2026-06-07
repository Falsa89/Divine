#!/usr/bin/env python3
# Track L: gate/runtime invariant preservation.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_psp_full_staging/v110_full_staging_gate_invariant_preservation_v1.json")
d = json.load(open(F))
assert d.get("battle_engine_formula_modified") is False
assert d.get("battle_simulate_route_invoked_from_staging") is False
assert d.get("battle_simulate_route_invoked_from_live") is False
assert d.get("validators_weakened") is False
assert d.get("validators_silently_deleted") is False
assert d.get("fake_PASS_introduced") is False
for k in ("postqa_d_gates_preserved", "server_isolation_v109_preserved",
          "v110_prep_preserved", "v110_apply_preflight_preserved",
          "v110_staging_smoke_pack72_preserved",
          "v110_staging_clone_pack73_preserved",
          "v110_staging_execute_pack74_preserved"):
    assert d.get(k) is True, k
ff = d.get("feature_flags_live_state", {})
for k in ("reward_live", "progress_live", "ledger_live", "battlepass_live",
          "vip_live", "shop_live", "gacha_live"):
    assert ff.get(k) is False, k
sf = d.get("safety_flags", {})
for k in ("battle_engine_formula_rewrite", "validator_weakening", "fake_PASS",
          "release_readiness_claimed", "postqa_d_unlocked"):
    assert sf.get(k) is False, k
print("[v110 FULL_STAGING_GATE_INVARIANT_PRESERVATION] OK gates/runtime preserved")
