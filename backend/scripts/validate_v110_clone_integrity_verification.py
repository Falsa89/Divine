#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_staging_clone/v110_clone_integrity_verification_v1.json")))
assert d.get("target_db_reachable") is True
assert d.get("marker_exists_in_target") is True
assert d.get("target_db_not_equal_source") is True
assert d.get("target_classification") == "STAGING_CLONE_CONFIRMED"
assert d.get("source_db_unchanged_at_collection_level") is True
assert d.get("users_count_match") is True, "users count must match between source and clone"
assert d.get("user_heroes_count_match") is True, "user_heroes count must match"
assert d.get("no_raw_secrets_exposed_in_artifacts") is True
for k in ("db_write_to_production", "fake_PASS", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False
print("[v110 CLONE_INTEGRITY_VERIFICATION] OK target=STAGING_CLONE_CONFIRMED users+user_heroes match source")
