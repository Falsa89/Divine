#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v78 Track A — Roadmap Realignment + Scope Lock."""
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
    realign = _load(ROOT / "data/design/release_acceleration/v78_roadmap_realignment_report_v1.json")
    scope = _load(ROOT / "data/design/economy/pve_reward_claim_canary_scope_lock_v1.json")
    forb = _load(ROOT / "data/design/economy/pve_reward_claim_canary_forbidden_scope_v1.json")
    marker = _load(ROOT / "data/design/release_acceleration/v78_roadmap_realignment_marker_v1.json")
    for name, obj in (("realign", realign), ("scope", scope), ("forb", forb), ("marker", marker)):
        if obj is None:
            ERR.append(f"missing:{name}")
    if realign:
        if realign.get("canonical_v78") != "pve_reward_claim_canary":
            ERR.append("realign.canonical_v78_invalid")
        if realign.get("previous_feedback_staging_pack_status") != "deferred_not_sent_or_do_not_execute_as_v78":
            ERR.append("realign.previous_feedback_staging_invalid")
        if realign.get("db_writes", 1) != 0:
            ERR.append("realign.db_writes_nonzero")
    if scope:
        must = ["pve_reward_claim_canary_scope", "non_premium_rewards_only", "allowlisted_canary_only",
                "apply_requires_isolated_staging", "dryrun_or_blocked_safe_if_missing_env",
                "idempotency_required", "ledger_required", "rollback_required", "observation_required"]
        for k in must:
            if scope.get(k) is not True:
                ERR.append(f"scope.{k}_not_true")
        forbidden_flags = ["premium_currency_allowed", "gacha_currency_allowed", "shop_vip_bp_allowed",
                           "arena_ranking_reward_allowed", "broad_rollout_allowed"]
        for k in forbidden_flags:
            if scope.get(k) is not False:
                ERR.append(f"scope.{k}_not_false")
    if forb:
        forb_types = forb.get("forbidden_reward_types", [])
        for t in ("premium_currency", "gacha_currency", "event_currency", "arena_points", "vip_points", "battle_pass_xp"):
            if t not in forb_types:
                ERR.append(f"forb.missing_type:{t}")
    if ERR:
        print("FAIL v78_roadmap_realignment:", "; ".join(ERR))
        return 1
    print("PASS v78_roadmap_realignment")
    return 0

if __name__ == "__main__":
    sys.exit(main())
