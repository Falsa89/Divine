#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v79 Track A — Staging Env Contract."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e:
        ERR.append(f"unreadable:{p}:{e}")
        return None

def main():
    env = _load(ROOT / "data/design/economy/pve_reward_claim_canary_staging_env_contract_v1.json")
    scope = _load(ROOT / "data/design/economy/pve_reward_claim_canary_staging_scope_lock_v1.json")
    forb = _load(ROOT / "data/design/economy/pve_reward_claim_canary_staging_forbidden_scope_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_canary_staging_env_marker_v1.json")
    for name, obj in (("env", env), ("scope", scope), ("forb", forb), ("marker", marker)):
        if obj is None:
            ERR.append(f"missing:{name}")
    if env:
        if env.get("staging_env_type") != "local_file_based":
            ERR.append("env.type_invalid")
        if env.get("staging_root") != "/app/data/canary_staging":
            ERR.append("env.root_invalid")
        for k in ("live_db_allowed", "real_user_accounts_allowed", "premium_currency_allowed",
                  "backend_route_exposure_allowed", "broad_rollout_allowed",
                  "mongo_url_used", "pymongo_used", "motor_used", "redis_used",
                  "asyncstorage_used", "asset_import"):
            if env.get(k) is not False:
                ERR.append(f"env.{k}_not_false")
        for k in ("local_ledger_only", "allowlist_required", "rollback_required",
                  "observation_required", "kill_switch_required"):
            if env.get(k) is not True:
                ERR.append(f"env.{k}_not_true")
    if scope:
        for k in ("applied_to_live", "live_reward_grant", "db_writes_allowed",
                  "backend_route_exposure", "battle_engine_change", "server_py_change",
                  "story_tsx_change", "combat_tsx_change", "asset_import",
                  "premium_currency_in_fixtures", "gacha_in_fixtures",
                  "shop_vip_bp_in_fixtures", "event_currency_in_fixtures",
                  "arena_ranking_in_fixtures", "pii_in_files"):
            if scope.get(k) is not False:
                ERR.append(f"scope.{k}_not_false")
        if scope.get("local_file_based_canary_only") is not True:
            ERR.append("scope.local_file_based_canary_only_not_true")
    if forb:
        for t in ("live_db_writes", "mongo_url_use", "pymongo_import", "motor_import",
                  "redis_use", "backend_route_registration", "server_py_change",
                  "battle_engine_change", "premium_currency", "asset_import", "env_mutation",
                  "fake_pass"):
            if t not in forb.get("forbidden_in_staging", []):
                ERR.append(f"forb.missing:{t}")
    if ERR:
        print("FAIL pve_reward_claim_canary_staging_env:", "; ".join(ERR))
        return 1
    print("PASS pve_reward_claim_canary_staging_env")
    return 0

if __name__ == "__main__":
    sys.exit(main())
