#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_migration/v110_server_id_filter_readiness_update_v1.json")))
assert d.get("prep_only") is True
assert d.get("server_id_filter_applied") is False, "v110 is prep-only; filter_applied must remain false"
assert d.get("real_player_team_source") is False
assert d.get("live_overall_ready") is False
assert d.get("preconditions_now_pass_after_v110") == []
still = set(d.get("preconditions_still_blocked_after_v110", []))
for must in ("server_id_filter_applied", "real_player_team_source", "psp_migration_readiness", "legacy_cleanup_readiness"):
    assert must in still, f"must still be blocked: {must}"
for k in ("false_filter_applied", "fake_PASS", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False, f"readiness safety {k}"
print("[v110 SERVER_ID_FILTER_READINESS_UPDATE] OK prep_only=true no_false_promotion live_overall_ready=false")
