#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_smoke/v110_staging_smoke_live_readiness_update_v1.json")))
assert d.get("production_filter_applied") is False
assert d.get("production_real_player_team_source") is False
assert d.get("live_overall_ready") is False
assert d.get("preconditions_now_pass_after_v110_staging_smoke") == []
still = set(d.get("preconditions_still_blocked_after_v110_staging_smoke", []))
for must in ("production_filter_applied", "production_real_player_team_source", "production_psp_migration_readiness", "production_legacy_cleanup_readiness"):
    assert must in still, f"must still be blocked {must}"
for k in ("false_production_filter_applied", "fake_PASS", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False
print("[v110 STAGING_SMOKE_LIVE_READINESS_UPDATE] OK no false production promotion")
