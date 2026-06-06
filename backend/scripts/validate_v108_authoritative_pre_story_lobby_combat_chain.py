#!/usr/bin/env python3
"""v108_AUTHORITATIVE_PRE - Track D chain audit validator."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "authoritative_pre", "v108_authoritative_pre_story_lobby_combat_chain_v1.json")
d = json.load(open(P))
chain = d.get("chain", [])
assert len(chain) == 3, "chain must have story/lobby/combat 3 nodes"
nodes = {c["node"] for c in chain}
assert nodes == {"story.tsx","pre-battle-lobby.tsx","combat.tsx"}, f"chain nodes mismatch {nodes}"
# Verify markers actually present in source
MARKERS = [
    ("frontend/app/story.tsx", "v108_pre"),
    ("frontend/app/pre-battle-lobby.tsx", "v107D"),
    ("frontend/app/pre-battle-lobby.tsx", "launch_context"),
    ("frontend/app/combat.tsx", "PREVIEW_REWARD_LOCK_ACTIVE"),
    ("frontend/app/combat.tsx", "launch_context"),
]
for rel, marker in MARKERS:
    full = os.path.join(ROOT, rel)
    assert os.path.isfile(full), f"missing {rel}"
    src = open(full).read()
    assert marker in src, f"marker {marker!r} missing in {rel}"
compat = d.get("authoritative_pre_compatibility", {})
assert compat.get("battle_instance_envelope_consumable_in_combat") is True
sf = d.get("safety_flags", {})
for k in ("calls_simulate_in_authoritative_pre","calls_refresh_user_in_authoritative_pre","calls_grant_affinity_in_authoritative_pre","fake_PASS","validator_weakening","release_readiness_claimed"):
    assert sf.get(k) is False, f"safety {k} must be false"
print("[v108_AUTHORITATIVE_PRE CHAIN_AUDIT] OK story->lobby->combat coherent envelope_compatible=true")
sys.exit(0)
