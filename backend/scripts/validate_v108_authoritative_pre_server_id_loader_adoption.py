#!/usr/bin/env python3
"""v108_AUTHORITATIVE_PRE - Track G server_id loader adoption."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "authoritative_pre", "v108_authoritative_pre_server_id_loader_adoption_v1.json")
d = json.load(open(P))
loaders = d.get("loaders", [])
assert len(loaders) >= 6, f"expected >=6 loaders, got {len(loaders)}"
# nessun loader puo' avere filter_applied=true (honest claim)
for l in loaders:
    assert l.get("filter_applied") is False, f"loader {l.get('loader')} must NOT claim filter_applied=true"
assert d.get("server_filter_applied_anywhere") is False
assert d.get("missing_server_id_blocks_battle_instance") is True
assert d.get("block_code_missing_server_id") == "BATTLE_INSTANCE_SERVER_REQUIRED"
assert d.get("server_isolation_live_claim") is False
assert d.get("psp_apply_done") is False
print("[v108_AUTHORITATIVE_PRE SERVER_ID_LOADER] OK honest filter_applied=false PSP=false isolation=false")
sys.exit(0)
