#!/usr/bin/env python3
import json,os,sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(R,"data/design/v109_server_isolation/v109_frontend_selected_server_propagation_audit_v1.json")))
surfaces=d.get("surfaces",[])
assert len(surfaces)>=3
assert d.get("frontend_runtime_filter_applied_claim") is False
print(f"[v109 FRONTEND_SELECTED_SERVER_PROPAGATION] OK surfaces={len(surfaces)} no_false_claim")
