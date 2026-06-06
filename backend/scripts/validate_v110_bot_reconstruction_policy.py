#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_migration/v110_bot_reconstruction_policy_v1.json")))
assert d.get("bots_default_disabled") is True
assert d.get("bots_server_scoped") is True
assert d.get("empty_roster_after_reset_forbidden") is True
assert d.get("legacy_heroes_in_bot_roster_forbidden") is True
assert d.get("premium_currency_grant_to_bots_forbidden") is True
opts = d.get("reconstruction_options_on_reset", [])
assert len(opts) >= 2
for o in opts:
    assert o.get("premium_grant") is False
    assert o.get("day1_lv100_forbidden") is True
for k in ("bots_default_startup", "bot_empty_roster_after_reset", "premium_grant", "fake_PASS", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False, f"bot safety {k}"
print(f"[v110 BOT_RECONSTRUCTION_POLICY] OK options={len(opts)} empty_roster_forbidden=true")
