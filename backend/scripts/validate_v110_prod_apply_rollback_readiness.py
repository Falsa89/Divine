#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_apply_execute/v110_prod_apply_rollback_readiness_v1.json")
d = json.load(open(F))
assert d.get("rollback_plan_present") is True
assert d.get("rollback_executed_on_production") is False
assert d.get("rollback_plan_targets_migration_marker") is True
assert d.get("rollback_readiness_ok") is True
steps = d.get("rollback_steps", [])
assert len(steps) >= 4
assert isinstance(d.get("emergency_stop_command"), str)
assert len(d.get("emergency_stop_command")) > 0
assert isinstance(d.get("psp_v110_marker_count_now"), int)
assert isinstance(d.get("user_heroes_with_server_id_s1_now"), int)
sf = d.get("safety_flags", {})
for k in ("rollback_executed_on_production", "destructive", "fake_PASS"):
    assert sf.get(k) is False, k
print(f"[v110 PROD_APPLY_ROLLBACK_READINESS] OK plan_present rollback_NOT_executed psp_marker_now={d.get('psp_v110_marker_count_now')}")
