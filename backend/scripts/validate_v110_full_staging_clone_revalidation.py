#!/usr/bin/env python3
# Track B: ri-valida che il target db sia il clone confermato.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_psp_full_staging/v110_full_staging_clone_revalidation_v1.json")
d = json.load(open(F))
assert d.get("classification") == "STAGING_CLONE_CONFIRMED"
assert d.get("active_db_for_apply") == "divine_waifus_staging_clone"
assert d.get("source_db") == "divine_waifus"
assert d.get("source_distinct_from_target") is True
assert d.get("production_apply") is False
assert d.get("production_marker_on_target") is False
assert d.get("safe_to_apply_full") is True
sf = d.get("safety_flags", {})
assert sf.get("production_apply") is False
assert sf.get("source_db_writes") is False
assert sf.get("fake_PASS") is False
assert sf.get("release_readiness_claimed") is False
print("[v110 FULL_STAGING_CLONE_REVALIDATION] OK STAGING_CLONE_CONFIRMED")
