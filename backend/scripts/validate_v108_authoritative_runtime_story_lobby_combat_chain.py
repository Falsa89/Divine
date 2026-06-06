#!/usr/bin/env python3
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "authoritative_runtime", "v108_authoritative_runtime_story_lobby_combat_chain_result_v1.json")
d = json.load(open(P))
assert d.get("resolve_preview_consumable_in_combat") is True
assert d.get("resolve_preview_required_combat_edits") is False
assert d.get("combat_calls_battle_simulate_in_staging") is False
for c in d.get("chain", []):
    assert c.get("calls_battle_simulate") is False, f"node {c.get('node')} must NOT call simulate"
MARKERS = [
    ("frontend/app/story.tsx", "v108_pre"),
    ("frontend/app/pre-battle-lobby.tsx", "v107D"),
    ("frontend/app/combat.tsx", "PREVIEW_REWARD_LOCK_ACTIVE"),
]
for rel, mk in MARKERS:
    full = os.path.join(ROOT, rel)
    assert os.path.isfile(full), f"missing {rel}"
    assert mk in open(full).read(), f"marker {mk} missing in {rel}"
sf = d.get("safety_flags", {})
for k in ("calls_simulate_in_staging","calls_refresh_user_in_staging","calls_grant_affinity_in_staging","fake_PASS","validator_weakening","release_readiness_claimed"):
    assert sf.get(k) is False
print("[v108_AUTHORITATIVE_RUNTIME CHAIN] OK story->lobby->combat staging-compatible no-simulate")
sys.exit(0)
