#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_preflight/v110_apply_preflight_live_readiness_update_v1.json")))
assert d.get("server_id_filter_applied") is False, "v110_apply_preflight is NOT executed; filter_applied must remain false"
assert d.get("real_player_team_source") is False
assert d.get("psp_migration_readiness") in ("DESIGN_READY_NOT_APPLIED", "PREP_READY_APPLY_GATED")
assert d.get("legacy_cleanup_readiness") == "NOT_READY"
assert d.get("live_overall_ready") is False
assert d.get("preconditions_now_pass_after_v110_apply_preflight") == []
still = set(d.get("preconditions_still_blocked_after_v110_apply_preflight", []))
for must in ("server_id_filter_applied", "real_player_team_source", "psp_migration_readiness", "legacy_cleanup_readiness"):
    assert must in still, f"must still be blocked: {must}"
for k in ("false_filter_applied", "fake_PASS", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False
print("[v110 APPLY_PREFLIGHT_LIVE_READINESS_UPDATE] OK no false promotion live_overall_ready=false")
