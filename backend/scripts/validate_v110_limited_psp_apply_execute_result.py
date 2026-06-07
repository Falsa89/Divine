#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_execute/v110_limited_psp_apply_execute_result_v1.json")))
assert d.get("status") == "APPLY_EXECUTED_STAGING_LIMITED"
assert d.get("apply_executed") is True
assert d.get("production_apply_executed") is False, "production apply MUST be false"
assert d.get("db_name") == "divine_waifus_staging_clone"
assert d.get("target_marker_present") is True
assert d.get("psp_inserted_in_this_run", 0) <= 10, "limited apply must not exceed --limit 10"
assert d.get("psp_inserted_in_this_run", 0) > 0, "apply should have inserted at least one PSP"
for k in ("db_write_to_production", "db_write_to_source", "destructive_migration", "premium_grant", "currency_duplication", "reward_live", "progress_live", "fake_PASS", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 LIMITED_PSP_APPLY_EXECUTE_RESULT] OK status={d['status']} psp_inserted={d.get('psp_inserted_in_this_run')} production_apply=false")
