#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_execute/v110_staging_revalidation_v1.json")))
assert d.get("classification") == "STAGING_CLONE_CONFIRMED"
assert d.get("marker_present") is True
assert d.get("safe_to_apply_limited") is True
assert d.get("source_db_distinct") is True
assert d.get("target_db") == "divine_waifus_staging_clone"
print("[v110 STAGING_REVALIDATION] OK target=divine_waifus_staging_clone marker_present=true")
