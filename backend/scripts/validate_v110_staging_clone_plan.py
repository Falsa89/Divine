#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_staging_clone/v110_staging_clone_plan_v1.json")))
assert d.get("target_db") != d.get("source_db"), "target must differ from source"
assert d.get("target_distinct_from_source") is True
assert d.get("target_db_name_contains_staging_or_clone") is True
assert d.get("no_production_writes") is True
assert isinstance(d.get("collections_to_clone"), list)
assert len(d.get("sensitive_fields_masked", [])) >= 4
aborts = d.get("abort_conditions", [])
for a in ("target_equal_source", "source_classification_production_or_unknown_without_approval"):
    assert a in aborts
for k in ("production_db_smoke", "fake_PASS", "premium_grant"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 STAGING_CLONE_PLAN] OK source={d['source_db']} target={d['target_db']} collections={len(d['collections_to_clone'])}")
