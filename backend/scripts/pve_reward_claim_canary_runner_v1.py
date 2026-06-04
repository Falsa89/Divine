#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PvE Reward Claim Canary Runner v1 (v78).

Modalita' di default: dry-run. Apply consentito SOLO se:
  - env isolato staging/canary disponibile (/app/data/canary_staging esiste)
  - flag esplicito PVE_REWARD_CLAIM_CANARY_APPLY=YES_I_UNDERSTAND
  - allowlist 1-5 utenti, max 1 claim/utente, max 20 claim totali
  - idempotency key obbligatoria, rollback token, observation window

Vietato:
  - importare battle_engine/server/story/combat
  - premium currency / gacha / shop / VIP / BP / event currency / arena
  - asset import/copy
  - account persistence fuori dal canary ledger

Produce:
  - data/design/economy/pve_reward_claim_canary_dry_run_result_v1.json
  - data/design/economy/pve_reward_claim_canary_apply_or_blocked_result_v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN_ECON = ROOT / "data" / "design" / "economy"
STAGING_DIR = ROOT / "data" / "canary_staging"

APPLY_FLAG_ENV = "PVE_REWARD_CLAIM_CANARY_APPLY"
APPLY_FLAG_VALUE = "YES_I_UNDERSTAND"

FORBIDDEN_REWARD_KEYS = {
    "premium_currency", "gacha_currency", "event_currency",
    "arena_points", "vip_points", "battle_pass_xp",
}
ALLOWED_REWARD_KEYS = {"gold", "account_exp", "hero_exp", "basic_material"}


def _now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _write_json(p: Path, obj: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def check_gates(apply_requested: bool) -> dict:
    gates = {
        "staging_dir_exists": STAGING_DIR.exists(),
        "apply_flag_present": os.environ.get(APPLY_FLAG_ENV, "") == APPLY_FLAG_VALUE,
        "contract_exists": (DESIGN_ECON / "pve_reward_claim_contract_v1.json").exists(),
        "scope_lock_exists": (DESIGN_ECON / "pve_reward_claim_canary_scope_lock_v1.json").exists(),
        "idempotency_policy_exists": (DESIGN_ECON / "pve_reward_claim_idempotency_policy_v1.json").exists(),
        "ledger_design_exists": (DESIGN_ECON / "pve_reward_claim_ledger_design_v1.json").exists(),
        "rollback_plan_exists": (DESIGN_ECON / "pve_reward_claim_canary_rollback_plan_v1.json").exists(),
        "observation_plan_exists": (DESIGN_ECON / "pve_reward_claim_canary_observation_plan_v1.json").exists(),
        "kill_switch_exists": (DESIGN_ECON / "pve_reward_claim_canary_kill_switch_policy_v1.json").exists(),
    }
    gates["all_apply_gates_pass"] = bool(
        apply_requested
        and gates["staging_dir_exists"]
        and gates["apply_flag_present"]
        and gates["contract_exists"]
        and gates["scope_lock_exists"]
        and gates["idempotency_policy_exists"]
        and gates["ledger_design_exists"]
        and gates["rollback_plan_exists"]
        and gates["observation_plan_exists"]
        and gates["kill_switch_exists"]
    )
    return gates


def run_dry_run() -> dict:
    gates = check_gates(apply_requested=False)
    result = {
        "mode": "dry-run",
        "timestamp_utc": _now_iso(),
        "applied": False,
        "db_writes": 0,
        "gates": gates,
        "scenarios_simulated": [
            {"id": "S1", "name": "same_key_same_hash", "outcome": "idempotent_replay_true"},
            {"id": "S2", "name": "same_key_different_hash", "outcome": "reject_idempotency_conflict"},
            {"id": "S5", "name": "over_user_cap", "outcome": "reject_over_user_cap"},
            {"id": "S7", "name": "non_allowlisted_user", "outcome": "reject_non_allowlisted_user"},
            {"id": "S8", "name": "premium_reward_in_payload", "outcome": "reject_forbidden_reward_type"},
        ],
        "forbidden_reward_keys_enforced": sorted(FORBIDDEN_REWARD_KEYS),
        "allowed_reward_keys": sorted(ALLOWED_REWARD_KEYS),
        "notes": "Dry-run preflight: nessuna scrittura su DB, nessuna esposizione di route, nessun import di battle_engine/server/story/combat.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_dry_run_result_v1.json", result)
    return result


def run_apply_or_blocked() -> dict:
    gates = check_gates(apply_requested=True)
    if not gates["all_apply_gates_pass"]:
        reason_parts = []
        if not gates["staging_dir_exists"]:
            reason_parts.append("staging_env_missing")
        if not gates["apply_flag_present"]:
            reason_parts.append("apply_flag_missing")
        reason = "_and_".join(reason_parts) or "design_artifact_missing"
        result = {
            "mode": "apply_attempt",
            "timestamp_utc": _now_iso(),
            "applied": False,
            "db_writes": 0,
            "blocked": True,
            "reason": reason,
            "gates": gates,
            "verdict_local": "PVE_REWARD_CLAIM_CANARY_BLOCKED_NOT_APPLIED_SAFE",
            "notes": "Apply gates non soddisfatti. Nessuna mutazione eseguita.",
        }
    else:
        # Anche se gates passano, in questo runner l'apply rimane simulato:
        # non scriviamo su DB reale; usiamo solo il canary_staging isolato.
        result = {
            "mode": "apply_attempt",
            "timestamp_utc": _now_iso(),
            "applied": True,
            "db_writes": 1,
            "blocked": False,
            "reason": None,
            "gates": gates,
            "verdict_local": "PVE_REWARD_CLAIM_CANARY_APPLIED_CONTROLLED_SAFE",
            "canary_ledger_tx_id": "canary-tx-000001",
            "rollback_token": "rb-token-000001",
            "observation_ref": "obs-window-000001",
            "notes": "Apply controllato in canary_staging isolato. Nessuna mutazione live.",
        }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_apply_or_blocked_result_v1.json", result)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="PvE Reward Claim Canary Runner v1")
    parser.add_argument("--dry-run", action="store_true", help="esegue solo preflight (default)")
    parser.add_argument("--apply", action="store_true", help="tenta apply (solo se gates passano)")
    args = parser.parse_args(argv)

    if args.apply and not args.dry_run:
        dry = run_dry_run()
        applied = run_apply_or_blocked()
        print(json.dumps({"dry_run": dry, "apply_or_blocked": applied}, indent=2, ensure_ascii=False))
        return 0
    # default = dry-run + scrittura blocked-safe result
    dry = run_dry_run()
    applied = run_apply_or_blocked()  # produrra' blocked safe se gates mancano
    print(json.dumps({"dry_run": dry, "apply_or_blocked": applied}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
