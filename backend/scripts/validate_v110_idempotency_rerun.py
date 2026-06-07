#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_execute/v110_idempotency_rerun_v1.json")))
assert d.get("idempotent_second_run_psp_inserts_zero") is True, "second run MUST insert zero new PSP"
assert d.get("idempotent_second_run_user_heroes_zero") is True, "second run MUST not re-set server_id on user_heroes"
assert d.get("duplicates_observed") == 0
first = d.get("first_run", {})
second = d.get("second_run", {})
assert first.get("psp_inserted", 0) > 0, "first run should have inserted PSP"
assert second.get("psp_inserted", -1) == 0, "second run psp_inserted must be 0"
for k in ("duplicate_psp", "db_write_to_production", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 IDEMPOTENCY_RERUN] OK first_inserts={first.get('psp_inserted')} second_inserts=0 duplicates=0")
