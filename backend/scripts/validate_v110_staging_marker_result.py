#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_staging_clone/v110_staging_marker_result_v1.json")))
assert d.get("marker_inserted_in_target") is True
assert d.get("marker_inserted_in_source") is False, "marker MUST NOT be inserted in source"
assert d.get("target_db") != d.get("source_db")
md = d.get("marker_document", {})
assert md.get("marker") == "v110_staging_clone_confirmed"
assert md.get("value") is True
assert md.get("production") is False
assert md.get("created_by_pack") == "MEGA_RELEASE_ACCELERATION_73_v110_PSP_STAGING_CLONE_PROVISION"
for k in ("false_staging_marker_on_production", "source_db_writes", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 STAGING_MARKER_RESULT] OK target_marker=true source_marker=false target={d['target_db']}")
