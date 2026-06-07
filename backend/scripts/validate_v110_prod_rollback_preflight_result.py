#!/usr/bin/env python3
# Pack 76 Track F: rollback/restore preflight (plan only).
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_preflight/v110_prod_rollback_preflight_result_v1.json")
d = json.load(open(F))
assert d.get("rollback_plan_present") is True
assert d.get("rollback_executed_on_production") is False
assert d.get("rollback_executed_in_this_pack") is False
assert d.get("rollback_targets_only_migration_marker") is True
assert d.get("rollback_preserves_pre_apply_user_data") is True
assert d.get("rollback_drill_validated_on_staging_clone_pack_75") is True
assert d.get("rollback_drill_dry_run_only_on_staging_pack_75") is False
assert d.get("rollback_drill_psp_deleted_on_staging_pack_75") == 1108
assert d.get("production_db_writes_during_preflight") == 0
assert isinstance(d.get("emergency_stop_command"), str) and len(d["emergency_stop_command"]) > 0
steps = d.get("rollback_steps", [])
assert len(steps) >= 4
for s in steps:
    assert s.get("destructive_on_production_pre_apply_data") is False
sf = d.get("safety_flags", {})
for k in ("rollback_executed_on_production", "destructive", "db_write_to_production", "fake_PASS"):
    assert sf.get(k) is False, k
print("[v110 PROD_ROLLBACK_PREFLIGHT] OK plan only, no execution on prod")
