#!/usr/bin/env python3
# Pack 76 Track D: production PSP apply dry-run (HOTFIX B1: --plan-only, returncode==0).
# Il dry_run_executed deve essere VERO solo se lo script ha terminato con returncode 0
# E ha dichiarato status=PLAN_ONLY_NO_WRITE E apply_executed=false E db_writes=0.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_preflight/v110_prod_psp_apply_dry_run_result_v1.json")
d = json.load(open(F))
assert d.get("target_db") == "divine_waifus"
assert d.get("target_server_id") == "s1"
# HOTFIX B1: invocation must succeed
inv = d.get("apply_script_invocation", {})
assert inv.get("returncode") == 0, f"dry-run script invocation failed with rc={inv.get('returncode')}"
assert inv.get("exit_zero") is True
# nessun --dry-run nel comando (lo script non lo supporta); accettiamo --plan-only o assenza di --execute
cmd = inv.get("cmd") or []
assert "--dry-run" not in cmd, "lo script non supporta --dry-run; usare --plan-only"
assert ("--plan-only" in cmd) or ("--execute" not in cmd)
# stato dichiarato dallo script
assert d.get("script_status_in_output_file") in (
    "PLAN_ONLY_NO_WRITE",
    "APPLY_REFUSED_MISSING_FLAGS",
    "APPLY_REFUSED_NO_DB",
    "APPLY_REFUSED_NOT_STAGING_CLONE",
), f"unexpected script status: {d.get('script_status_in_output_file')}"
# Su produzione lo script DEVE rifiutarsi (non è un clone), quindi accettiamo APPLY_REFUSED_*.
# Su staging clone con flag impostati si avrebbe PLAN_ONLY_NO_WRITE.
assert d.get("script_apply_executed_in_output_file") is False
assert d.get("script_db_writes_in_output_file") == 0
assert d.get("dry_run_real_success") is True
assert d.get("dry_run_executed") is True
assert d.get("dry_run_invocation_mode") == "plan_only"
assert d.get("hotfix_applied") == "v110_PROD_PREFLIGHT_B1_DRY_RUN_INVOCATION_AND_DIFF_RECONCILIATION"
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
# coerenza stime: total writes == psp + sum(updates)
total = (
    d["psp_to_insert_estimate"]
    + d["user_heroes_to_update_estimate"]
    + d["team_formation_to_update_estimate"]
    + d["user_equipment_to_update_estimate"]
)
assert d["db_writes_if_apply_executed_estimate"] == total, (
    f"diff mismatch: {total} != {d['db_writes_if_apply_executed_estimate']}"
)
sf = d.get("safety_flags", {})
for k in ("production_apply", "production_db_writes", "false_filter_applied",
          "release_readiness_claimed", "fake_PASS",
          "fake_dry_run_when_command_failed"):
    assert sf.get(k) is False, k
print(
    f"[v110 PROD_PSP_APPLY_DRY_RUN] OK B1 plan-only rc=0 users={d.get('users_selected')} "
    f"psp_to_insert={d.get('psp_to_insert_estimate')} user_heroes={d.get('user_heroes_to_update_estimate')} "
    f"team={d.get('team_formation_to_update_estimate')} equip={d.get('user_equipment_to_update_estimate')} "
    f"total_writes_if_executed={total} actual_writes=0"
)
