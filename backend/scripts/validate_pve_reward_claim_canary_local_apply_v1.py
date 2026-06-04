#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v79 Track D — Local Apply Result."""
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
    pre = _load(ROOT / "data/design/economy/pve_reward_claim_canary_staging_preflight_result_v1.json")
    apply_r = _load(ROOT / "data/design/economy/pve_reward_claim_canary_local_apply_result_v1.json")
    apply_or_blk = _load(ROOT / "data/design/economy/pve_reward_claim_canary_staging_apply_or_blocked_result_v1.json")
    snap = _load(ROOT / "data/design/economy/pve_reward_claim_canary_staging_ledger_snapshot_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_canary_local_apply_marker_v1.json")
    for name, obj in (("pre", pre), ("apply_r", apply_r), ("apply_or_blk", apply_or_blk),
                       ("snap", snap), ("marker", marker)):
        if obj is None:
            ERR.append(f"missing:{name}")
    if apply_r:
        if apply_r.get("applied_to_live") is not False:
            ERR.append("apply_r.applied_to_live_not_false")
        if apply_r.get("db_writes", 1) != 0:
            ERR.append("apply_r.db_writes_nonzero")
        if apply_r.get("live_reward_grant") is not False:
            ERR.append("apply_r.live_reward_grant_not_false")
        if apply_r.get("applied_to_local_staging") not in (True, False):
            ERR.append("apply_r.applied_to_local_staging_missing")
        if apply_r.get("applied_to_local_staging") is True:
            if not isinstance(apply_r.get("local_file_writes"), int) or apply_r["local_file_writes"] <= 0:
                ERR.append("apply_r.local_file_writes_invalid_when_applied")
            if apply_r.get("verdict_local") != "PVE_REWARD_CLAIM_CANARY_LOCAL_STAGING_APPLIED_SAFE":
                ERR.append("apply_r.verdict_invalid_when_applied")
    if snap:
        if snap.get("db_writes", 1) != 0:
            ERR.append("snap.db_writes_nonzero")
        if snap.get("live_reward_grant") is not False:
            ERR.append("snap.live_reward_grant_not_false")
        if snap.get("premium_in_ledger") is not False:
            ERR.append("snap.premium_in_ledger_not_false")
        if snap.get("pii_in_ledger") is not False:
            ERR.append("snap.pii_in_ledger_not_false")
    if ERR:
        print("FAIL pve_reward_claim_canary_local_apply:", "; ".join(ERR))
        return 1
    print("PASS pve_reward_claim_canary_local_apply")
    return 0

if __name__ == "__main__":
    sys.exit(main())
