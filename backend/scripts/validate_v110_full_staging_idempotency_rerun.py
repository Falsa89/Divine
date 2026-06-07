#!/usr/bin/env python3
# Track E: rerun completo idempotente, 0 duplicati.
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_psp_full_staging/v110_full_staging_idempotency_rerun_v1.json")
d = json.load(open(F))
assert d.get("second_run_new_profiles_inserted") == 0
assert d.get("idempotent_second_run_psp_inserts_zero") is True
assert d.get("duplicate_profile_ids") == 0
assert d.get("duplicate_user_id_server_id_pairs") == 0
assert d.get("source_db_writes") == 0
assert d.get("production_db_writes") == 0
sr = d.get("second_run", {})
assert sr.get("psp_inserted") == 0
sf = d.get("safety_flags", {})
assert sf.get("duplicate_psp") is False
assert sf.get("db_write_to_production") is False
assert sf.get("fake_PASS") is False
print("[v110 FULL_STAGING_IDEMPOTENCY_RERUN] OK second_run inserts=0 duplicates=0")
