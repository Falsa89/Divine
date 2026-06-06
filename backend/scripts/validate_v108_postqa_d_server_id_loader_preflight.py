#!/usr/bin/env python3
"""v108_POSTQA_D - Track F server_id loader preflight validator."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "postqa", "v108_postqa_d_server_id_loader_preflight_v1.json")
d = json.load(open(P))
assert d.get("sentinel") == "PUBLIC_SYNC_TAG_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS"
st = d.get("server_id_loader_state", {})
assert st.get("filter_applied") is False, "filter_applied claim must be false (honest)"
assert st.get("server_scope_runtime_active") is False
assert "backend/utils/server_scope.py" in st.get("server_scope_helper", "")
sf = d.get("safety_flags", {})
assert sf.get("server_id_filter_claim_unless_real") is False
print("[v108_POSTQA_D SERVER_ID_LOADER_PREFLIGHT] OK filter_applied=false honest")
sys.exit(0)
