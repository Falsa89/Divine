#!/usr/bin/env python3
"""v108_POSTQA_D - Track B legacy mutation gate policy validator."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "postqa", "v108_postqa_d_legacy_mutation_gate_policy_v1.json")
assert os.path.isfile(P), f"missing {P}"
d = json.load(open(P))
assert d.get("sentinel") == "PUBLIC_SYNC_TAG_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS"
eps = d.get("endpoints", [])
assert len(eps) == 23, f"expected 23 endpoints in watchlist, got {len(eps)}"

REQUIRED = {
    "/api/hero/gain-exp",
    "/api/hero/levelup",
    "/api/fusion/star-up",
    "/api/soul/forge",
    "/api/vip/add-spend",
    "/api/battlepass/buy-premium",
    "/api/friends/gift",
    "/api/gvg/end-war",
    "/api/equipment/equip",
}
mapped = {e["endpoint"]: e for e in eps}
for r in REQUIRED:
    assert r in mapped, f"endpoint {r} not in watchlist policy"
    assert mapped[r]["target_state"] == "blocked_by_default", f"{r} not blocked_by_default"
    assert mapped[r]["gate"].startswith("DIVINE_ALLOW_LEGACY_"), f"{r} gate must be DIVINE_ALLOW_LEGACY_*"
assert d.get("new_endpoints_with_default_off_gate") == 9
sf = d.get("safety_flags", {})
for k in ("fake_PASS", "validator_weakening", "silent_validator_deletion", "release_readiness_claimed"):
    assert sf.get(k) is False
print("[v108_POSTQA_D LEGACY_GATE_POLICY] OK watchlist=23 high_risk_default_off=9")
sys.exit(0)
