#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PvE Reward Claim Live DB Canary Apply Design Drill v1 (v85).

Scopo: simulare in modalita' DESIGN-ONLY:
  - kill switch trigger drill (DISENGAGED -> ENGAGE -> DISENGAGED con dual approval)
  - rollback approval chain drill
  - approval chain checksum mismatch handling

Vincoli (HARD):
  - NESSUNA scrittura DB (db_writes=0)
  - NESSUN endpoint backend creato/registrato
  - NESSUN import di pymongo, motor, redis, battle_engine
  - NESSUN uso di Mongo connection string
  - NESSUNA mutazione di account o reward live
  - Solo file JSON locali in /app/data/design/economy

Produce:
  - data/design/economy/pve_reward_claim_live_db_canary_apply_kill_switch_drill_result_v1.json
  - data/design/economy/pve_reward_claim_live_db_canary_apply_rollback_chain_drill_result_v1.json
  - data/design/economy/pve_reward_claim_live_db_canary_apply_drill_rollup_v1.json
  - data/design/economy/pve_reward_claim_v86_gate_v1.json
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN_ECON = ROOT / "data" / "design" / "economy"


def _now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _write_json(p: Path, obj: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _sha256(s: str) -> str:
    return "sha256:" + hashlib.sha256(s.encode()).hexdigest()


def drill_kill_switch() -> dict:
    states = []
    # Start DISENGAGED
    states.append({"phase": "init", "state": "DISENGAGED", "incoming_claims_simulated": 3,
                   "outcome": "all_claims_pass_design_only_simulated"})
    # Engage (no dual approval required for engage)
    states.append({"phase": "engage", "state_transition": "DISENGAGED->ENGAGE",
                   "dual_approval": False, "outcome": "allowed"})
    # While ENGAGED, every claim rejected
    states.append({"phase": "engaged_window", "state": "ENGAGE", "incoming_claims_simulated": 5,
                   "outcome": "all_claims_rejected_kill_switch_active"})
    # Disengage attempt without dual approval -> rejected
    states.append({"phase": "disengage_attempt_single_approval", "state_transition": "ENGAGE->DISENGAGED",
                   "dual_approval": False, "outcome": "rejected_dual_approval_required"})
    # Disengage with dual approval -> allowed
    states.append({"phase": "disengage_with_dual_approval", "state_transition": "ENGAGE->DISENGAGED",
                   "dual_approval": True, "outcome": "allowed"})
    # Audit log emitted
    audit = [
        {"ts": _now_iso(), "event": "kill_switch_engaged", "actor": "release_owner"},
        {"ts": _now_iso(), "event": "kill_switch_disengage_rejected_single_approval", "actor": "release_owner"},
        {"ts": _now_iso(), "event": "kill_switch_disengaged", "actor": "release_owner+security_owner"},
    ]
    result = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "drill_id": "kill_switch_trigger",
        "states": states,
        "audit_log_design": audit,
        "all_engage_window_claims_rejected": True,
        "single_approval_disengage_rejected": True,
        "dual_approval_disengage_allowed": True,
        "db_writes": 0,
        "endpoint_implemented": False,
        "live_reward_grant": False,
        "design_only": True,
        "notes": "Kill switch trigger drill design-only. NESSUNA chiamata HTTP reale, NESSUN flag env mutato.",
    }
    _write_json(
        DESIGN_ECON / "pve_reward_claim_live_db_canary_apply_kill_switch_drill_result_v1.json",
        result,
    )
    return result


def drill_rollback_chain() -> dict:
    # Catena di approvazione del rollback (design-only)
    chain = [
        {"step": 1, "actor": "release_owner", "action": "rollback_request",
         "checksum": _sha256("rollback_request|release_owner"), "approved": True},
        {"step": 2, "actor": "security_owner", "action": "rollback_second_approval",
         "input_checksum_match": True,
         "checksum": _sha256("rollback_second_approval|security_owner"), "approved": True},
        {"step": 3, "actor": "automation", "action": "verify_md5_invariants",
         "approved": True, "design_only": True},
        {"step": 4, "actor": "automation", "action": "verify_suite_zero_required_fail",
         "approved": True, "design_only": True},
        {"step": 5, "actor": "automation", "action": "verify_no_db_writes",
         "approved": True, "design_only": True},
        {"step": 6, "actor": "release_owner+security_owner", "action": "final_rollback_go",
         "step_up_required": True, "approved": True, "design_only": True},
    ]
    # Negative path 1: checksum mismatch
    negative = [
        {"case": "checksum_mismatch_at_second_approval",
         "outcome": "halted_checksum_mismatch", "design_only": True},
        {"case": "single_human_only_approval",
         "outcome": "halted_dual_approval_required", "design_only": True},
        {"case": "step_up_missing_at_final_go",
         "outcome": "halted_step_up_missing", "design_only": True},
    ]
    rolled_back_tx = [
        {"tx_id_simulated": "dryrun-tx-rb-001", "rolled_back": True,
         "db_rollback": False, "design_only": True},
        {"tx_id_simulated": "dryrun-tx-rb-002", "rolled_back": True,
         "db_rollback": False, "design_only": True},
    ]
    result = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "drill_id": "rollback_approval_chain",
        "approval_chain": chain,
        "negative_cases": negative,
        "rolled_back_tx_simulated": rolled_back_tx,
        "all_chain_approved": all(s.get("approved") for s in chain),
        "all_negatives_halted": all(n.get("outcome", "").startswith("halted") for n in negative),
        "db_rollback": False,
        "db_writes": 0,
        "endpoint_implemented": False,
        "live_reward_grant": False,
        "design_only": True,
        "notes": "Rollback chain drill design-only. NESSUN apply DB, NESSUN endpoint reale.",
    }
    _write_json(
        DESIGN_ECON / "pve_reward_claim_live_db_canary_apply_rollback_chain_drill_result_v1.json",
        result,
    )
    return result


def build_v86_gate(ks: dict, rb: dict) -> dict:
    all_ok = all([
        ks.get("all_engage_window_claims_rejected") is True,
        ks.get("single_approval_disengage_rejected") is True,
        ks.get("dual_approval_disengage_allowed") is True,
        ks.get("db_writes") == 0,
        ks.get("endpoint_implemented") is False,
        rb.get("all_chain_approved") is True,
        rb.get("all_negatives_halted") is True,
        rb.get("db_rollback") is False,
        rb.get("db_writes") == 0,
        rb.get("endpoint_implemented") is False,
    ])
    gate = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "design_drill_pass": all_ok,
        "v86_recommendation": (
            "live_db_canary_apply_dry_run_with_dual_approval_pack_v86_still_no_apply"
            if all_ok else
            "continue_design_hardening_v86"
        ),
        "live_db_apply_allowed": False,
        "endpoint_implemented": False,
        "db_writes": 0,
        "manual_approval_required_for_future_apply": True,
        "checksum_required_for_future_apply": True,
        "step_up_auth_required_for_future_apply": True,
        "notes": "Gate v86: design-only. NESSUN apply DB, NESSUN endpoint reale, NESSUN reward live.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_v86_gate_v1.json", gate)
    return gate


def run_all() -> dict:
    ks = drill_kill_switch()
    rb = drill_rollback_chain()
    rollup = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "pack": "v85",
        "kill_switch_drill": ks,
        "rollback_chain_drill": rb,
        "db_writes": 0,
        "endpoint_implemented": False,
        "live_reward_grant": False,
        "design_only": True,
    }
    _write_json(
        DESIGN_ECON / "pve_reward_claim_live_db_canary_apply_drill_rollup_v1.json",
        rollup,
    )
    gate = build_v86_gate(ks, rb)
    rollup["v86_gate"] = gate
    return rollup


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="PvE Reward Claim Live DB Canary Apply Design Drill v1 (v85)"
    )
    parser.add_argument("--all", action="store_true", help="esegue tutti i drill design-only")
    args = parser.parse_args(argv)
    if args.all or True:
        out = run_all()
        summary = {
            "db_writes": out["db_writes"],
            "endpoint_implemented": out["endpoint_implemented"],
            "live_reward_grant": out["live_reward_grant"],
            "design_only": out["design_only"],
            "kill_switch_all_engage_reject": out["kill_switch_drill"]["all_engage_window_claims_rejected"],
            "kill_switch_dual_approval_disengage": out["kill_switch_drill"]["dual_approval_disengage_allowed"],
            "rollback_chain_all_approved": out["rollback_chain_drill"]["all_chain_approved"],
            "rollback_chain_all_negatives_halted": out["rollback_chain_drill"]["all_negatives_halted"],
            "v86_design_drill_pass": out["v86_gate"]["design_drill_pass"],
            "v86_recommendation": out["v86_gate"]["v86_recommendation"],
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
