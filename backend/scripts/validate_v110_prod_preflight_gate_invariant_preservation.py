#!/usr/bin/env python3
# Pack 76 Track L: gate/runtime invariant preservation.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_preflight/v110_prod_preflight_gate_invariant_preservation_v1.json")
d = json.load(open(F))
assert d.get("battle_engine_formula_modified") is False
assert d.get("battle_simulate_route_invoked_from_staging") is False
assert d.get("battle_simulate_route_invoked_from_live") is False
assert d.get("validators_weakened") is False
assert d.get("validators_silently_deleted") is False
assert d.get("fake_PASS_introduced") is False
assert d.get("approval_flags_changed_to_yes") is False
for k in ("postqa_d_gates_preserved", "server_isolation_v109_preserved",
          "v110_prep_preserved", "v110_apply_preflight_preserved",
          "v110_staging_smoke_pack72_preserved",
          "v110_staging_clone_pack73_preserved",
          "v110_staging_execute_pack74_preserved",
          "v110_full_staging_pack75_preserved"):
    assert d.get(k) is True, k
ff = d.get("feature_flags_live_state", {})
for k in ("reward_live", "progress_live", "ledger_live", "battlepass_live",
          "vip_live", "shop_live", "gacha_live"):
    assert ff.get(k) is False, k
flags = d.get("approval_flags_state", {})
for flag in ("V110_PSP_APPLY", "V110_BACKUP_CONFIRMED",
             "V110_USER_EXPLICIT_DB_WRITE_APPROVAL",
             "V110_ROLLBACK_PLAN_CONFIRMED",
             "V110_PRODUCTION_DB_EXPLICIT_APPROVAL"):
    assert flags.get(flag) != "YES", flag
sf = d.get("safety_flags", {})
for k in ("battle_engine_formula_rewrite", "validator_weakening", "fake_PASS",
          "release_readiness_claimed", "postqa_d_unlocked",
          "approval_flags_changed_to_yes"):
    assert sf.get(k) is False, k
print("[v110 PROD_PREFLIGHT_GATE_INVARIANT_PRESERVATION] OK preserved")
