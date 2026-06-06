#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_migration/v110_account_global_vs_server_scoped_matrix_v1.json")))
ents = d.get("entities", [])
assert len(ents) >= 20, f"matrix expects >=20 entities, got {len(ents)}"
for e in ents:
    assert e.get("scope") and e.get("entity"), "entity must have scope and name"
assert d.get("premium_currency_account_global") is True
assert d.get("soft_currency_server_scoped") is True
assert d.get("applied_in_this_pack") is False
assert d.get("db_writes") == 0
assert d.get("safety_flags", {}).get("premium_currency_grant") is False
assert d.get("safety_flags", {}).get("false_filter_applied") is False
print(f"[v110 ACCOUNT_GLOBAL_VS_SERVER_SCOPED_MATRIX] OK entities={len(ents)} applied=false")
