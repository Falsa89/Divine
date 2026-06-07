#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_server_filter_team_source/backend_route_probe_smoke_v1.json")
d = json.load(open(F))
probes = d.get("probes", [])
assert isinstance(probes, list) and len(probes) >= 5
for p in probes:
    if "error" in p: continue
    assert p.get("status_code") == 200, p
    assert p.get("server_id_received_in_payload") == "s1"
    assert p.get("filter_applied_in_payload") is False
assert d.get("all_probes_returned_filter_applied_false") is True
assert d.get("no_probe_returned_filter_applied_true") is True
sf = d.get("safety_flags", {})
assert sf.get("false_filter_applied_true") is False
assert sf.get("fake_PASS") is False
print(f"[v110 BACKEND_ROUTE_PROBE_SMOKE] OK {len(probes)} probes, all filter_applied=false")
