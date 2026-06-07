#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_staging_clone/v110_pack72_readiness_recheck_v1.json")))
assert d.get("classification") == "STAGING_CLONE_CONFIRMED"
assert d.get("safe_to_apply_limited") is True
assert d.get("production_apply") is False
assert "divine_waifus_staging_clone" in d.get("target_db", "")
assert "divine_waifus_staging_clone" in d.get("recommended_next_command", "")
for k in ("production_apply", "fake_PASS", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 PACK72_READINESS_RECHECK] OK target={d['target_db']} classification=STAGING_CLONE_CONFIRMED safe_to_apply_limited=true")
