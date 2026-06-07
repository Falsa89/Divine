#!/usr/bin/env python3
# Pack 76 Track K: live readiness post-preflight.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_preflight/v110_prod_preflight_live_readiness_update_v1.json")
d = json.load(open(F))
assert d.get("production_dry_run_executed") is True
assert d.get("production_backup_preflight_executed") is True
assert d.get("production_rollback_preflight_executed") is True
assert d.get("production_apply_executed") is False
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
pre = d.get("preconditions_for_production_apply", {})
for k in ("psp_full_staging_apply_green", "psp_full_staging_idempotent",
          "psp_full_staging_rollback_real_executed", "psp_full_staging_source_immutable",
          "production_dry_run_executed", "production_backup_preflight_executed",
          "production_rollback_preflight_executed", "production_apply_script_safety_audited"):
    assert pre.get(k) is True, k
assert pre.get("production_explicit_user_approval") is False
assert pre.get("V110_PRODUCTION_DB_EXPLICIT_APPROVAL_set_to_YES") is False
assert "production_apply_execute_pack" in d.get("next_step", "").lower()
sf = d.get("safety_flags", {})
for k in ("production_apply_executed", "production_db_writes", "reward_live",
          "progress_live", "fake_PASS", "release_readiness_claimed"):
    assert sf.get(k) is False, k
print("[v110 PROD_PREFLIGHT_LIVE_READINESS_UPDATE] OK live OFF, next=apply_execute_pack")
