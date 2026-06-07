#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_execute/v110_staging_execute_live_readiness_update_v1.json")))
assert d.get("production_filter_applied") is False
assert d.get("live_overall_ready") is False
assert d.get("preconditions_now_pass_after_v110_staging_execute") == []
for k in ("false_production_filter_applied", "fake_PASS", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False
print("[v110 STAGING_EXECUTE_LIVE_READINESS_UPDATE] OK no production promotion live_overall_ready=false")
