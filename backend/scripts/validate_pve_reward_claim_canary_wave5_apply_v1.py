#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v83 Track D — Wave5 Apply + Replay + Negative Tests."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    apply_res = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave5_apply_result_v1.json")
    blocked_res = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave5_apply_or_blocked_result_v1.json")
    apply_marker = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave5_apply_marker_v1.json")
    neg = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave5_replay_negative_test_result_v1.json")
    ledger = _load(ROOT / "data/canary_staging/wave5_local_ledger_v1.json")
    snap = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave5_ledger_snapshot_v1.json")

    for name, obj in (("apply_res", apply_res), ("blocked_res", blocked_res),
                      ("apply_marker", apply_marker), ("neg", neg),
                      ("ledger", ledger), ("snap", snap)):
        if obj is None: ERR.append(f"missing:{name}")

    if apply_res:
        if apply_res.get("applied_to_live") is not False: ERR.append("apply.applied_to_live_not_false")
        if apply_res.get("db_writes") != 0: ERR.append("apply.db_writes_not_0")
        if apply_res.get("live_reward_grant") is not False: ERR.append("apply.live_reward_grant_not_false")
        if apply_res.get("verdict_local") != "PVE_REWARD_CLAIM_CANARY_WAVE5_OBSERVED_SAFE":
            ERR.append("apply.verdict_invalid")
        if apply_res.get("wave5_success_count", 0) < 1:
            ERR.append("apply.wave5_success_count_zero")
        if apply_res.get("wave5_max_claims_total") != 12:
            ERR.append("apply.wave5_max_claims_total_not_12")

    if neg:
        tests = {t.get("test") for t in neg.get("negative_tests", [])}
        required = {
            "duplicate_idempotency_replay",
            "duplicate_conflicting_hash",
            "non_allowlisted_user",
            "premium_reward_reject",
            "over_cap_reward_reject",
            "malformed_route_reject",
            "event_arena_ranking_reward_reject",
            "real_account_id_reject",
        }
        missing = required - tests
        for m in sorted(missing): ERR.append(f"neg.missing_test:{m}")
        if neg.get("all_negative_tests_passed") is not True:
            ERR.append("neg.not_all_passed")
        if neg.get("db_writes") != 0: ERR.append("neg.db_writes_not_0")

    if ledger:
        if not isinstance(ledger.get("entries"), list) or len(ledger["entries"]) < 1:
            ERR.append("ledger.entries_empty")
        if len(ledger.get("entries", [])) > 12:
            ERR.append("ledger.entries_over_12")
        for e in ledger.get("entries", []):
            if e.get("wave") != 5: ERR.append("ledger.entry_wave_not_5")
            payload = e.get("reward_payload_summary", {})
            for forb_k in ("premium_currency", "gacha_currency", "event_currency",
                           "arena_points", "arena_ranking_reward", "vip_points", "battle_pass_xp"):
                if forb_k in payload:
                    ERR.append(f"ledger.entry_forbidden_key:{forb_k}")

    if snap:
        if snap.get("db_writes") != 0: ERR.append("snap.db_writes_not_0")
        if snap.get("live_reward_grant") is not False: ERR.append("snap.live_reward_grant_not_false")
        if snap.get("premium_in_ledger") is not False: ERR.append("snap.premium_in_ledger_not_false")
        if snap.get("pii_in_ledger") is not False: ERR.append("snap.pii_in_ledger_not_false")

    if ERR:
        print("FAIL pve_reward_claim_canary_wave5_apply:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_canary_wave5_apply"); return 0

if __name__ == "__main__": sys.exit(main())
