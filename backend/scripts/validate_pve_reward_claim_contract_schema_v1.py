#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v78 Track B — PvE Reward Claim Contract + Request/Response Schema."""
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
    contract = _load(ROOT / "data/design/economy/pve_reward_claim_contract_v1.json")
    req = _load(ROOT / "data/design/economy/pve_reward_claim_request_schema_v1.json")
    resp = _load(ROOT / "data/design/economy/pve_reward_claim_response_schema_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_contract_marker_v1.json")
    for name, obj in (("contract", contract), ("req", req), ("resp", resp), ("marker", marker)):
        if obj is None:
            ERR.append(f"missing:{name}")
    if contract:
        if contract.get("claim_source") != "pve":
            ERR.append("contract.claim_source_not_pve")
        allowed = set(contract.get("allowed_rewards", []))
        if allowed != {"gold", "account_exp", "hero_exp", "basic_material"}:
            ERR.append("contract.allowed_rewards_mismatch")
        forb = set(contract.get("forbidden_rewards", []))
        for t in ("premium_currency", "gacha_currency", "event_currency", "arena_points", "vip_points", "battle_pass_xp"):
            if t not in forb:
                ERR.append(f"contract.forbidden_missing:{t}")
        if contract.get("requires_isolated_staging") is not True:
            ERR.append("contract.requires_isolated_staging_not_true")
        if contract.get("db_writes_default", 1) != 0:
            ERR.append("contract.db_writes_default_nonzero")
    if req:
        req_fields = req.get("request_fields", {})
        for f in ("user_id", "server_id", "route_id", "run_id", "claim_id", "idempotency_key", "reward_hash", "reward_payload"):
            if f not in req_fields:
                ERR.append(f"req.missing_field:{f}")
    if resp:
        resp_fields = resp.get("response_fields", {})
        for f in ("applied", "idempotent_replay", "rejected_reason", "ledger_tx_id", "rollback_token", "observation_ref", "db_writes"):
            if f not in resp_fields:
                ERR.append(f"resp.missing_field:{f}")
    if ERR:
        print("FAIL pve_reward_claim_contract_schema:", "; ".join(ERR))
        return 1
    print("PASS pve_reward_claim_contract_schema")
    return 0

if __name__ == "__main__":
    sys.exit(main())
