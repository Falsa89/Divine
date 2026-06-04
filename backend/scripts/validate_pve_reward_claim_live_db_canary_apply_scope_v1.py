#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v85 Track B — Canary Apply Scope Lock (design-only)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    scope = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_canary_apply_scope_lock_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_canary_apply_scope_marker_v1.json")
    for name, obj in (("scope", scope), ("marker", marker)):
        if obj is None: ERR.append(f"missing:{name}")
    if scope:
        for k in ("design_only", "still_no_apply", "no_real_account_mutation",
                  "no_premium_currency", "no_arena_ranking_reward",
                  "no_production_ui_exposure", "alias_only",
                  "future_apply_requires_new_pack",
                  "manual_approval_required_for_future_apply",
                  "checksum_required_for_future_apply"):
            if scope.get(k) is not True: ERR.append(f"scope.{k}_not_true")
        for k in ("live_db_apply_allowed", "endpoint_implemented", "live_reward_grant",
                  "mongo_url_used", "pymongo_used", "motor_used", "redis_used"):
            if scope.get(k) is not False: ERR.append(f"scope.{k}_not_false")
        if scope.get("db_writes") != 0: ERR.append("scope.db_writes_not_0")
    if marker:
        if marker.get("design_only") is not True: ERR.append("marker.design_only_not_true")
        if marker.get("still_no_apply") is not True: ERR.append("marker.still_no_apply_not_true")
        if marker.get("db_writes") != 0: ERR.append("marker.db_writes_not_0")
    if ERR:
        print("FAIL pve_reward_claim_live_db_canary_apply_scope:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_live_db_canary_apply_scope"); return 0

if __name__ == "__main__": sys.exit(main())
