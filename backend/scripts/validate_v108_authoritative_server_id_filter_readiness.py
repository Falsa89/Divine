#!/usr/bin/env python3
import json,os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(ROOT,"data","design","authoritative_live_preconditions","v108_authoritative_server_id_filter_readiness_v1.json")))
loaders=d.get("loaders",[])
assert len(loaders)>=9
for l in loaders:
    assert l.get("filters_server_id") is False, f"loader {l.get('loader')} claims filter_applied=true (forbidden honest claim)"
    assert l.get("filter_applied_claim_allowed") is False
assert d.get("any_loader_filter_applied_true") is False
assert d.get("live_ready") is False
assert d.get("live_blocked_because_any_account_wide_loader") is True
for k in ("false_server_id_filter_claim","server_isolation_live_claim","fake_PASS","validator_weakening","release_readiness_claimed"):
    assert d.get("safety_flags",{}).get(k) is False
print("[v108_AUTHORITATIVE_SERVER_ID_FILTER_READINESS] OK loaders>=9 honest_no_false_claim live_ready=false")
sys.exit(0)
