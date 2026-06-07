#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_staging_clone/v110_source_db_classification_v1.json")))
s = d.get("source", {})
assert s.get("classification") in ("STAGING_CLONE_CONFIRMED", "LOCAL_CONTAINER_NON_PROD")
assert s.get("is_production") is False
assert s.get("safe_to_clone_from") is True
assert d.get("backup_before_clone_required") is True
for k in ("production_db_smoke", "fake_PASS", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 SOURCE_DB_CLASSIFICATION] OK classification={s['classification']} safe_to_clone_from=true")
