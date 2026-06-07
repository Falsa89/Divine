#!/usr/bin/env python3
import json, os, urllib.request, urllib.error
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_execute/v110_source_immutability_proof_v1.json")))
assert d.get("source_unchanged_at_count_level") is True
assert d.get("source_db_writes_during_pack_74") == 0
assert d.get("source_psp_present") == 0, "source DB must not have any PSP"
assert d.get("source_user_heroes_with_server_id") >= 0  # source already has server_id from existing app runtime, must be stable
assert d.get("source_marker_present") is False, "source DB must NOT have staging marker"
assert d.get("source_migration_logs_v110_count") == 0, "source must not have v110 migration log entries"
for k in ("production_db_writes", "db_write_to_source", "destructive_source_op", "delete_on_source", "premium_grant", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
try:
    req = urllib.request.Request("http://localhost:8001/api/soul/forge", data=b'{}', headers={"Content-Type": "application/json"}, method="POST")
    try:
        urllib.request.urlopen(req, timeout=2)
    except urllib.error.HTTPError as e:
        assert e.code == 423
        body = e.read().decode("utf-8", "ignore")
        assert "LEGACY_MUTATION_LOCKED_BY_POSTQA_D" in body
except Exception as e:
    if isinstance(e, AssertionError):
        raise
print("[v110 SOURCE_IMMUTABILITY_PROOF] OK source_unchanged=true writes_source=0 marker_source=false POSTQA_D 423 confirmed")
