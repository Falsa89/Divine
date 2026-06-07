#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_execute/v110_pre_apply_snapshot_v1.json")))
assert d.get("read_only") is True
for k in ("db_write", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
assert "source_snapshot" in d and "staging_snapshot" in d
assert d["source_snapshot"].get("users") >= 1
print("[v110 PRE_APPLY_SNAPSHOT] OK source/staging snapshots captured read_only=true")
