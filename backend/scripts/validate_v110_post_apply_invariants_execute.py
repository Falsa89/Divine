#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_execute/v110_post_apply_invariants_v1.json")))
c = d.get("checks", {})
assert d.get("all_invariants_ok") is True
for k in ("psp_count_le_limit_10", "no_duplicate_psp_user_server", "users_count_unchanged", "user_heroes_count_unchanged", "no_team_size_drift", "no_legacy_delete", "no_premium_grant", "no_currency_duplication"):
    assert c.get(k, {}).get("ok") is True, f"invariant {k} failed"
for k in ("premium_grant", "currency_duplication", "fake_PASS", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False
print("[v110 POST_APPLY_INVARIANTS_EXECUTE] OK all_invariants_ok=true 8/8 checks passed")
