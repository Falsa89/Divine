#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v80 Track D — Wave2 Apply Result + Snapshot + Negative Tests."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    apply_r = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave2_apply_result_v1.json")
    snap = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave2_ledger_snapshot_v1.json")
    neg = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave2_replay_negative_test_result_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave2_apply_marker_v1.json")
    for name, obj in (("apply_r", apply_r), ("snap", snap), ("neg", neg), ("marker", marker)):
        if obj is None: ERR.append(f"missing:{name}")
    if apply_r:
        if apply_r.get("applied_to_live") is not False: ERR.append("apply_r.applied_to_live_not_false")
        if apply_r.get("db_writes", 1) != 0: ERR.append("apply_r.db_writes_nonzero")
        if apply_r.get("live_reward_grant") is not False: ERR.append("apply_r.live_reward_grant_not_false")
        if not isinstance(apply_r.get("wave2_success_count"), int):
            ERR.append("apply_r.wave2_success_count_missing")
        if apply_r.get("applied_to_local_staging") is True:
            if apply_r.get("verdict_local") != "PVE_REWARD_CLAIM_CANARY_WAVE2_OBSERVED_SAFE":
                ERR.append("apply_r.verdict_invalid_when_applied")
            if apply_r.get("wave2_success_count", 0) < 1 or apply_r.get("wave2_success_count", 0) > 3:
                ERR.append("apply_r.wave2_success_count_out_of_range")
    if snap:
        if snap.get("db_writes", 1) != 0: ERR.append("snap.db_writes_nonzero")
        if snap.get("live_reward_grant") is not False: ERR.append("snap.live_reward_grant_not_false")
        if snap.get("premium_in_ledger") is not False: ERR.append("snap.premium_in_ledger_not_false")
        if snap.get("pii_in_ledger") is not False: ERR.append("snap.pii_in_ledger_not_false")
    if neg:
        if neg.get("all_negative_tests_passed") is not True:
            ERR.append("neg.all_negative_tests_passed_not_true")
        if neg.get("db_writes", 1) != 0: ERR.append("neg.db_writes_nonzero")
        tests_names = {t.get("test") for t in neg.get("negative_tests", [])}
        required = {"duplicate_idempotency_replay", "duplicate_conflicting_hash",
                    "non_allowlisted_user", "premium_reward_reject", "over_cap_reward_reject"}
        missing = required - tests_names
        if missing: ERR.append(f"neg.missing_tests:{sorted(missing)}")
    if ERR:
        print("FAIL pve_reward_claim_canary_wave2_apply:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_canary_wave2_apply"); return 0

if __name__ == "__main__": sys.exit(main())
