#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_preflight/v110_apply_implementation_contract_v1.json")))
assert d.get("algorithm_version")
src = d.get("source_collections", [])
for must in ("users", "user_heroes", "team_formation", "user_inventory", "user_equipment", "battlepass_progress", "vip_progress", "user_mail", "achievements", "story_progress"):
    assert must in src, f"contract source must include {must}"
assert d.get("target_collection") == "player_server_profiles"
assert d.get("profile_id_format") == "{account_id}:{server_id}"
assert d.get("default_server_id_policy", {}).get("default_server_id")
fields = d.get("psp_fields_inserted", {})
for f in ("user_id", "server_id", "profile_id", "created_at", "player_level", "soft_currencies", "migration_source"):
    assert f in fields, f"contract field {f}"
assert d.get("economy_strategy", {}).get("premium_grant_forbidden") is True
assert d.get("economy_strategy", {}).get("duplication_forbidden") is True
assert d.get("collision_idempotency_strategy", {}).get("upsert") is True
assert d.get("collision_idempotency_strategy", {}).get("duplicate_psp_forbidden") is True
assert d.get("collision_idempotency_strategy", {}).get("re_run_safe") is True
aborts = d.get("safety_aborts", [])
for a in ("backup_marker_missing", "premium_balance_mismatch", "duplicate_psp_detected", "team_size_changed", "any_premium_grant_attempt"):
    assert a in aborts, f"safety_abort {a}"
assert d.get("applied_in_this_pack") is False
assert d.get("db_writes") == 0
print(f"[v110 APPLY_IMPLEMENTATION_CONTRACT] OK version={d['algorithm_version']} aborts={len(aborts)}")
