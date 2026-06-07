#!/usr/bin/env python3
# Pack 76 Track B: classificazione ambiente produzione (read-only).
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_prod_preflight/v110_production_environment_classification_v1.json")
d = json.load(open(F))
assert d.get("target_db") == "divine_waifus"
assert d.get("classification") == "PRODUCTION_LIKE_LOCAL_CONTAINER"
assert d.get("is_distinct_from_staging_clone") is True
assert d.get("staging_clone_marker_on_target") is False
assert d.get("production_apply_intended_in_this_pack") is False
assert d.get("dry_run_only") is True
assert d.get("read_only_for_target") is True
assert d.get("safe_to_dry_run") is True
sf = d.get("safety_flags", {})
for k in ("production_apply", "production_db_writes", "fake_PASS", "release_readiness_claimed"):
    assert sf.get(k) is False, k
print("[v110 PROD_ENV_CLASSIFICATION] OK PRODUCTION_LIKE_LOCAL_CONTAINER read-only")
