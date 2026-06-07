#!/usr/bin/env python3
# Pack 76 Track D: production PSP apply dry-run (no scritture).
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_preflight/v110_prod_psp_apply_dry_run_result_v1.json")
d = json.load(open(F))
assert d.get("target_db") == "divine_waifus"
assert d.get("target_server_id") == "s1"
assert d.get("dry_run_executed") is True
assert d.get("apply_executed") is False
assert d.get("production_apply_executed") is False
assert d.get("actual_db_writes_in_this_dry_run") == 0
assert d.get("production_db_writes") == 0
assert d.get("no_premium_grant") is True
assert d.get("no_deletes") is True
assert d.get("no_reward_live") is True
assert d.get("no_progress_live") is True
assert d.get("no_marker_inserted") is True
assert d.get("no_migration_logs_inserted") is True
assert d.get("no_psp_inserted") is True
assert d.get("no_server_id_set_on_legacy_collections") is True
for k in ("users_selected", "psp_count_pre_apply", "psp_to_insert_estimate",
          "user_heroes_to_update_estimate", "team_formation_to_update_estimate",
          "user_equipment_to_update_estimate", "db_writes_if_apply_executed_estimate"):
    assert isinstance(d.get(k), int), k
assert d.get("users_selected") >= 1
sf = d.get("safety_flags", {})
for k in ("production_apply", "production_db_writes", "false_filter_applied",
          "release_readiness_claimed", "fake_PASS"):
    assert sf.get(k) is False, k
print(f"[v110 PROD_PSP_APPLY_DRY_RUN] OK users={d.get('users_selected')} psp_to_insert={d.get('psp_to_insert_estimate')} writes=0")
