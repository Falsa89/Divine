#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(R, "data/design/v110_psp_apply_staging_smoke/v110_environment_classification_v1.json")
assert os.path.isfile(P)
d = json.load(open(P))
assert d.get("classification") in ("STAGING_CLONE_CONFIRMED", "LOCAL_CONTAINER_NON_PROD", "PRODUCTION_OR_UNSAFE", "UNKNOWN")
assert d.get("db_writes") == 0
assert d.get("safety_flags", {}).get("production_db_smoke") is False
assert d.get("safety_flags", {}).get("fake_PASS") is False
# Onesta: safe_to_apply solo se STAGING_CLONE_CONFIRMED
expected_safe = d.get("classification") == "STAGING_CLONE_CONFIRMED"
assert d.get("safe_to_apply") is expected_safe, "safe_to_apply must mirror STAGING_CLONE_CONFIRMED honestly"
print(f"[v110 STAGING_SMOKE_ENV_CLASSIFICATION] OK classification={d['classification']} safe_to_apply={d['safe_to_apply']}")
