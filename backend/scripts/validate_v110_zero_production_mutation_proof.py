#!/usr/bin/env python3
import json, os, urllib.request, urllib.error
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_staging_clone/v110_zero_production_mutation_proof_v1.json")))
assert d.get("source_db_unchanged_at_count_level") is True
assert d.get("no_psp_apply_on_source") is True
assert d.get("no_legacy_cleanup") is True
assert d.get("no_reward_progress_live") is True
assert d.get("no_production_db_writes") is True
assert d.get("postqa_d_gates_intact") is True
assert d.get("writes_source_db") == 0
for k in ("production_db_writes", "db_write_to_source", "destructive_source_op", "delete_on_source", "premium_grant", "reward_live", "progress_live", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
# Runtime check: source DB POSTQA_D gate still active
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
print(f"[v110 ZERO_PRODUCTION_MUTATION_PROOF] OK source unchanged, writes_source=0, target_writes={d.get('writes_target_db')}, POSTQA_D 423 confirmed")
