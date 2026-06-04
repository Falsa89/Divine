#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v84 Track B — Live DB Dry-Run Scope Lock."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    scope = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_dry_run_scope_lock_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_dry_run_scope_marker_v1.json")
    for name, obj in (("scope", scope), ("marker", marker)):
        if obj is None: ERR.append(f"missing:{name}")
    if scope:
        if scope.get("dry_run_only") is not True: ERR.append("scope.dry_run_only_not_true")
        if scope.get("live_db_apply_allowed") is not False: ERR.append("scope.live_db_apply_allowed_not_false")
        if scope.get("endpoint_implemented") is not False: ERR.append("scope.endpoint_implemented_not_false")
        if scope.get("db_writes") != 0: ERR.append("scope.db_writes_not_0")
        if scope.get("live_reward_grant") is not False: ERR.append("scope.live_reward_grant_not_false")
        for k in ("no_real_account_mutation", "no_premium_currency", "no_arena_ranking_reward",
                  "alias_only", "manual_approval_required_for_future_apply",
                  "checksum_required_for_future_apply"):
            if scope.get(k) is not True: ERR.append(f"scope.{k}_not_true")
        for k in ("mongo_url_used", "pymongo_used", "motor_used", "redis_used", "production_ui_exposure"):
            if scope.get(k) is not False: ERR.append(f"scope.{k}_not_false")
    if marker:
        if marker.get("dry_run_only") is not True: ERR.append("marker.dry_run_only_not_true")
        if marker.get("db_writes") != 0: ERR.append("marker.db_writes_not_0")
    if ERR:
        print("FAIL pve_reward_claim_live_db_dry_run_scope:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_live_db_dry_run_scope"); return 0

if __name__ == "__main__": sys.exit(main())
