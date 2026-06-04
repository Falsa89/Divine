#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v78 Track C — Idempotency + Ledger + Replay."""
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
    idemp = _load(ROOT / "data/design/economy/pve_reward_claim_idempotency_policy_v1.json")
    ledger = _load(ROOT / "data/design/economy/pve_reward_claim_ledger_design_v1.json")
    replay = _load(ROOT / "data/design/economy/pve_reward_claim_replay_scenario_matrix_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_idempotency_ledger_marker_v1.json")
    for name, obj in (("idemp", idemp), ("ledger", ledger), ("replay", replay), ("marker", marker)):
        if obj is None:
            ERR.append(f"missing:{name}")
    if idemp:
        pol = idemp.get("policy", {})
        for k in ("same_key_same_hash", "same_key_different_hash", "missing_key", "expired_key",
                  "claim_over_user_cap", "claim_over_total_cap", "non_allowlisted_user"):
            if k not in pol:
                ERR.append(f"idemp.policy_missing:{k}")
    if ledger:
        fields = set(ledger.get("fields", []))
        for f in ("tx_id", "user_id_hash", "server_id", "claim_id", "route_id", "reward_hash",
                  "reward_payload_summary", "rollback_token", "created_at", "canary"):
            if f not in fields:
                ERR.append(f"ledger.missing_field:{f}")
        if ledger.get("pii") is not False:
            ERR.append("ledger.pii_not_false")
        if ledger.get("premium_fields") is not False:
            ERR.append("ledger.premium_fields_not_false")
    if replay:
        scen = replay.get("scenarios", [])
        if len(scen) < 7:
            ERR.append("replay.scenarios_too_few")
    if ERR:
        print("FAIL pve_reward_claim_idempotency_ledger:", "; ".join(ERR))
        return 1
    print("PASS pve_reward_claim_idempotency_ledger")
    return 0

if __name__ == "__main__":
    sys.exit(main())
