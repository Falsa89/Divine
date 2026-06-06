#!/usr/bin/env python3
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "authoritative_runtime", "v108_authoritative_runtime_battle_result_envelope_schema_v1.json")
d = json.load(open(P))
SENT = "PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_BATTLE_RUNTIME_STAGING_NO_REWARD_LIVE"
assert d.get("sentinel") == SENT
assert d.get("schema_version") == "battle_result_envelope_v1"
fields = {f["name"]: f for f in d.get("fields", [])}
for must in ("battle_instance_id","server_id","mode","authoritative_live","authoritative_staging","battle_engine_mode","winner","turn_log","player_team_result","enemy_team_result","reward_policy","progress_policy","rewards.granted","rewards.preview_only","progress.written","progress.preview_only","safety.db_writes_allowed","safety.db_writes_performed","safety.reward_live_enabled","safety.progress_live_enabled","safety.calls_legacy_mutating_endpoints","safety.calls_battle_simulate_endpoint","safety.battle_engine_formula_rewritten","safety.server_filter_applied"):
    assert must in fields, f"field missing: {must}"
assert fields["authoritative_live"].get("fixed_value") is False
assert fields["authoritative_staging"].get("fixed_value") is True
assert fields["battle_engine_mode"].get("fixed_value") == "authoritative_staging"
blocks = set(d.get("block_codes", []))
for c in ("BATTLE_RESULT_INSTANCE_REQUIRED","BATTLE_RESULT_AUTHORITATIVE_LIVE_FORBIDDEN","BATTLE_RESULT_REWARD_LIVE_FORBIDDEN","BATTLE_RESULT_PROGRESS_LIVE_FORBIDDEN","BATTLE_RESULT_PLAYER_TEAM_REQUIRED","BATTLE_RESULT_ENEMY_TEAM_REQUIRED","BATTLE_RESULT_LEGACY_SIMULATE_FORBIDDEN"):
    assert c in blocks, f"block missing: {c}"
print("[v108_AUTHORITATIVE_RUNTIME RESULT_ENVELOPE_SCHEMA] OK fields_ok block_codes=7 authoritative_live=false authoritative_staging=true")
sys.exit(0)
