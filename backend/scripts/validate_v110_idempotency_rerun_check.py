#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_smoke/v110_idempotency_rerun_check_v1.json")))
assert d.get("physical_duplicate_psp_observed") == 0
assert d.get("physical_extra_inserts_observed") == 0
assert d.get("db_writes") == 0
tc = d.get("theoretical_contract_re_asserted", {})
assert tc.get("unique_key") == ["user_id", "server_id"]
assert tc.get("upsert_non_destructive_on_collision") is True
assert tc.get("second_run_inserts_zero") is True
for k in ("duplicate_psp", "db_write", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 IDEMPOTENCY_RERUN_CHECK] OK status={d.get('status')} duplicates=0 extras=0")
