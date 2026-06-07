#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_staging_clone/v110_staging_clone_execution_result_v1.json")))
assert d.get("executed") is True
assert d.get("source_db") != d.get("target_db")
assert d.get("source_writes") == 0, "source DB must NEVER be written"
assert d.get("target_writes_total_inserted_docs", 0) > 0, "clone must have actually inserted docs into target"
for k in ("source_db_writes", "db_write_to_production", "premium_grant", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 STAGING_CLONE_EXECUTION_RESULT] OK target_inserted={d['target_writes_total_inserted_docs']} source_writes=0 errors={d.get('target_writes_total_errors', 0)}")
