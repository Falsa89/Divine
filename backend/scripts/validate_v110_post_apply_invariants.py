#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_smoke/v110_post_apply_invariants_v1.json")))
c = d.get("checks", {})
for k in ("psp_delta_matches_limit_or_zero", "unique_profile_id_holds", "premium_balance_diff", "hard_balance_diff", "soft_balance_aggregated_per_user", "team_size_diff", "no_legacy_delete", "no_premium_grant", "no_currency_duplication"):
    assert c.get(k, {}).get("ok") is True, f"invariant {k} not ok"
assert d.get("all_invariants_ok") is True
assert d.get("db_writes") == 0
for k in ("premium_grant", "currency_duplication", "fake_PASS", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False
print("[v110 POST_APPLY_INVARIANTS] OK all_invariants_ok=true db_writes=0")
