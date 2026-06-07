#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_server_filter_team_source/backend_loader_server_id_filter_promotion_matrix_v1.json")
d = json.load(open(F))
assert d.get("honest_audit") is True
assert d.get("false_filter_applied_anywhere") is False
assert d.get("filter_applied_any_real_loader") is False
assert isinstance(d.get("loaders", []), list) and len(d["loaders"]) >= 5
for l in d["loaders"]:
    assert l.get("filter_applied") is False
    assert l.get("real_loader_query_filters_by_server_id") is False
    assert isinstance(l.get("promotion_status"), str) and l["promotion_status"].startswith("DEFERRED")
sf = d.get("safety_flags", {})
assert sf.get("false_filter_applied_true") is False
assert sf.get("fake_PASS") is False and sf.get("validator_weakening") is False
print(f"[v110 LOADER_FILTER_PROMOTION_MATRIX] OK deferred={d.get('deferred_count')} promoted={d.get('promoted_count')}")
