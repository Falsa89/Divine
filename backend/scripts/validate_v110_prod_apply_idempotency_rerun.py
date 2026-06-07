#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_apply_execute/v110_prod_apply_idempotency_rerun_v1.json")
d = json.load(open(F))
assert d.get("second_run_returncode") == 0
assert d.get("second_run_script_status") == "APPLY_EXECUTED_PRODUCTION"
assert d.get("second_run_psp_inserted") == 0
assert d.get("second_run_user_heroes_set") == 0
assert d.get("second_run_team_set") == 0
assert d.get("second_run_equipment_set") == 0
assert d.get("duplicate_profile_pairs") == 0
assert d.get("idempotent_second_run_psp_inserts_zero") is True
assert d.get("idempotent_second_run_user_heroes_zero") is True
sf = d.get("safety_flags", {})
assert sf.get("duplicate_psp") is False
assert sf.get("fake_PASS") is False
print(f"[v110 PROD_APPLY_IDEMPOTENCY_RERUN] OK second_run inserts=0 duplicates=0 total_after={d.get('psp_total_after_idempotency')}")
