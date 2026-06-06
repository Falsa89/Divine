#!/usr/bin/env python3
import json,os,sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,"data/design/v109_server_isolation/v109_core_loader_filter_promotion_v1.json")))
loaders=d.get("loaders",[])
assert len(loaders)>=7
for l in loaders:
    assert l.get("filter_applied_claim") is False, f"loader {l.get('loader')} false filter_applied claim"
assert d.get("any_loader_promoted") is False
assert d.get("filter_applied_anywhere_true") is False
print(f"[v109 CORE_LOADER_FILTER_PROMOTION] OK loaders={len(loaders)} honest no_false_claim")
