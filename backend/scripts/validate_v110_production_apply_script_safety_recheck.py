#!/usr/bin/env python3
# Pack 76 Track I: production apply script safety recheck.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_preflight/v110_production_apply_script_safety_recheck_v1.json")
d = json.load(open(F))
assert d.get("all_audits_ok") is True
assert d.get("production_db_writes_during_audit") == 0
assert d.get("script_modified_in_this_pack") is False
audits = d.get("audits", {})
for k in ("execute_flag_required", "v110_psp_apply_env_required",
          "v110_backup_confirmed_env_required",
          "v110_user_explicit_db_write_approval_env_required",
          "v110_rollback_plan_confirmed_env_required",
          "v110_staging_db_confirmed_env_required",
          "dry_run_is_default",
          "no_path_writes_production_without_explicit_flag",
          "no_path_executes_apply_without_target_server_id"):
    assert audits.get(k) is True, k
sha = d.get("apply_script_sha256")
assert isinstance(sha, str) and len(sha) == 64
sf = d.get("safety_flags", {})
for k in ("fake_PASS", "destructive", "production_apply"):
    assert sf.get(k) is False, k
print("[v110 PROD_APPLY_SCRIPT_SAFETY_RECHECK] OK all gates required")
