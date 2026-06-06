#!/usr/bin/env python3
"""v108_AUTHORITATIVE_PRE - Track B envelope schema validator."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "authoritative_pre", "v108_authoritative_pre_battle_instance_envelope_schema_v1.json")
d = json.load(open(P))
SENT = "PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_PRE_BATTLE_INSTANCE_STAGING_NO_REWARD_LIVE"
assert d.get("sentinel") == SENT
assert d.get("schema_version") == "battle_instance_envelope_v1"
fields = {f["name"]: f for f in d.get("fields", [])}
for required in ("battle_instance_id","server_id","mode","player_team_snapshot","enemy_source_type","enemy_source_id","battle_engine_mode","authoritative_live","reward_policy","progress_policy","safety","idempotency_key"):
    assert required in fields, f"field missing: {required}"
assert fields["authoritative_live"].get("fixed_value") is False
blocks = set(d.get("block_codes", []))
for c in ("BATTLE_INSTANCE_SERVER_REQUIRED","BATTLE_INSTANCE_PLAYER_TEAM_REQUIRED","BATTLE_INSTANCE_ENEMY_SOURCE_REQUIRED","BATTLE_INSTANCE_REWARD_LIVE_FORBIDDEN","BATTLE_INSTANCE_PROGRESS_LIVE_FORBIDDEN"):
    assert c in blocks, f"block code missing: {c}"
assert d.get("safety_flags", {}).get("authoritative_live_claim") is False
print("[v108_AUTHORITATIVE_PRE ENVELOPE_SCHEMA] OK fields_ok block_codes=5 authoritative_live=false")
sys.exit(0)
