#!/usr/bin/env python3
# Track K: live readiness rimane disabilitato.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_psp_full_staging/v110_full_staging_live_readiness_update_v1.json")
d = json.load(open(F))
assert d.get("production_apply") is False
assert d.get("production_filter_applied") is False
assert d.get("live_overall_ready") is False
assert d.get("release_readiness_claimed") is False
assert d.get("rollup_pass_does_not_imply_release_readiness") is True
for k in ("reward_live_enabled", "progress_live_enabled", "ledger_live_enabled",
          "battle_pass_live_enabled", "vip_live_enabled", "shop_live_enabled",
          "gacha_live_enabled", "v108_postqa_d_gates_unlocked"):
    assert d.get(k) is False, k
pre = d.get("preconditions_for_production_apply", {})
assert pre.get("psp_full_staging_apply_green") is True
assert pre.get("psp_full_staging_idempotent") is True
assert pre.get("psp_full_staging_rollback_real_executed") is True
assert pre.get("psp_full_staging_source_immutable") is True
assert pre.get("production_dry_run_executed") is False
assert pre.get("all_17_live_preconditions_pass") is False
assert "production_dry_run" in d.get("next_step", "").lower()
sf = d.get("safety_flags", {})
for k in ("production_apply_executed", "production_db_writes", "reward_live",
          "progress_live", "fake_PASS", "release_readiness_claimed"):
    assert sf.get(k) is False, k
print("[v110 FULL_STAGING_LIVE_READINESS_UPDATE] OK live OFF, next=prod_dry_run")
