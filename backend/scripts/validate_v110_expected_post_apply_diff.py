#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_preflight/v110_expected_post_apply_diff_v1.json")))
assert d.get("expected_psp_inserts_full_run", 0) >= 850, "expected_psp_inserts_full_run must align with dry-run accounts count"
assert d.get("expected_psp_inserts_per_user") == 1
assert d.get("expected_users_deleted") == 0
assert d.get("no_premium_grant") is True
assert d.get("no_source_deletion") is True
assert d.get("team_constraints", {}).get("team_size_preserved") == 6
assert d.get("team_constraints", {}).get("no_fake_team_creation") is True
cs = d.get("currency_split_enforced", {})
assert cs.get("soft_currencies_moved_to_psp_per_user") is True
assert cs.get("hard_currencies_stay_users_doc") is True
assert cs.get("premium_currencies_stay_users_doc") is True
assert d.get("bot_constraints", {}).get("no_empty_roster_after_reset") is True
assert d.get("bot_constraints", {}).get("no_premium_grant_to_bots") is True
assert d.get("db_writes_in_this_pack") == 0
assert d.get("apply_executed_in_this_pack") is False
for k in ("premium_grant", "source_deletion", "fake_team", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 EXPECTED_POST_APPLY_DIFF] OK expected_psp_inserts={d['expected_psp_inserts_full_run']} apply_executed=false")
