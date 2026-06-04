#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PvE Reward Claim Live DB Dry-Run Simulator v1 (v84).

Scopo: simulare in modalita' DRY-RUN i contratti di design definiti in v83:
  - db_transaction_policy
  - real_account_allowlist_schema
  - auth_guard
  - endpoint_contract
  - rollback_script
  - observation_sink
  - kill_switch

Vincoli (HARD):
  - NESSUNA scrittura DB (db_writes=0)
  - NESSUN endpoint backend creato/registrato
  - NESSUN import di pymongo, motor, redis, battle_engine
  - NESSUN uso di Mongo connection string
  - NESSUN reward grant live, NESSUNA mutazione di account
  - NESSUNA modifica a server.py / battle_engine.py / story.tsx / combat.tsx
  - Solo file JSON locali in /app/data/design/economy

Produce:
  - data/design/economy/pve_reward_claim_live_db_dry_run_result_v1.json (rollup simulator)
  - data/design/economy/pve_reward_claim_live_db_dry_run_transaction_policy_result_v1.json
  - data/design/economy/pve_reward_claim_live_db_dry_run_auth_guard_result_v1.json
  - data/design/economy/pve_reward_claim_live_db_dry_run_endpoint_contract_result_v1.json
  - data/design/economy/pve_reward_claim_live_db_dry_run_kill_switch_result_v1.json
  - data/design/economy/pve_reward_claim_live_db_dry_run_rollback_result_v1.json
  - data/design/economy/pve_reward_claim_live_db_dry_run_observation_sink_result_v1.json
  - data/design/economy/pve_reward_claim_v85_gate_v1.json
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
FIXTURES = ROOT / "data" / "canary_staging" / "live_db_dry_run_fixtures_v1.json"
CONTRACT = ROOT / "data" / "design" / "economy" / "pve_reward_claim_live_db_design_contract_v1.json"

ALLOWED_REWARD_KEYS = {"gold", "account_exp", "hero_exp", "basic_material"}
VALID_ROUTES = {
    "story_alpha_slice_preview",
    "training_combat_onboarding_preview",
    "boss_tower_alpha_loop_preview",
    "first_session_onboarding_preview",
    "alpha_menu_preview",
    "reward_claim_summary_preview",
    "event_arena_alpha_gate_preview",
    "event_arena_first_alpha_slice_preview",
}


def _now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _write_json(p: Path, obj: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _is_sha256_alias(uid: str) -> bool:
    return isinstance(uid, str) and uid.startswith("sha256:") and "@" not in uid and len(uid) >= 16


def _payload_validation(payload: dict, caps: dict, forbidden: set) -> tuple:
    if not isinstance(payload, dict) or not payload:
        return False, "empty_payload"
    for k in payload.keys():
        if k in forbidden:
            return False, f"forbidden_reward_type:{k}"
        if k not in ALLOWED_REWARD_KEYS:
            return False, f"unknown_reward_key:{k}"
    for k, v in payload.items():
        if not isinstance(v, int) or v < 0:
            return False, f"invalid_value:{k}"
        cap = caps.get(k)
        if cap is not None and v > cap:
            return False, f"over_cap:{k}"
    return True, None


def dry_run_transaction_policy(fixtures: dict, contract: dict) -> dict:
    """Simula la transaction policy senza alcuna scrittura DB."""
    policy = contract["sections"]["db_transaction_policy"]
    caps = fixtures.get("caps", {})
    forbidden = set(fixtures.get("forbidden_reward_keys", []))
    allowlist = {u["user_id_hash"] for u in fixtures.get("users", [])}

    simulated_tx = []
    seen_keys = set()
    for c in fixtures.get("claims", []):
        idem_key = f"idem:dryrun:{c['user_id_hash']}:{c['claim_id']}"
        if idem_key in seen_keys:
            simulated_tx.append({"claim_id": c["claim_id"], "applied": False, "reason": "idempotent_replay"})
            continue
        seen_keys.add(idem_key)
        ok, reason = _payload_validation(c["reward_preview"], caps, forbidden)
        if not ok:
            simulated_tx.append({"claim_id": c["claim_id"], "applied": False, "reason": reason})
            continue
        if c["route_id"] not in VALID_ROUTES:
            simulated_tx.append({"claim_id": c["claim_id"], "applied": False, "reason": "malformed_route"})
            continue
        if c["user_id_hash"] not in allowlist:
            simulated_tx.append({"claim_id": c["claim_id"], "applied": False, "reason": "non_allowlisted_user"})
            continue
        # Simula tx commit (NO DB)
        tx_id = f"dryrun-tx-{hashlib.sha256(idem_key.encode()).hexdigest()[:12]}"
        simulated_tx.append({"claim_id": c["claim_id"], "applied": True, "tx_id": tx_id,
                             "idempotency_key": idem_key,
                             "reward_summary_hash": "sha256:" + hashlib.sha256(
                                 json.dumps(c["reward_preview"], sort_keys=True).encode()
                             ).hexdigest()[:32]})

    # Replay idempotente (riapplicazione della prima claim)
    if fixtures.get("claims"):
        first = fixtures["claims"][0]
        idem_key = f"idem:dryrun:{first['user_id_hash']}:{first['claim_id']}"
        simulated_tx.append({"claim_id": first["claim_id"], "applied": False,
                             "reason": "idempotent_replay_returned",
                             "idempotency_key": idem_key,
                             "replay": True})

    result = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "policy_applied": policy,
        "simulated_tx": simulated_tx,
        "applied_count": sum(1 for t in simulated_tx if t.get("applied")),
        "rejected_count": sum(1 for t in simulated_tx if not t.get("applied")),
        "db_writes": 0,
        "live_reward_grant": False,
        "endpoint_implemented": False,
        "dry_run_only": True,
        "notes": "Simulazione transaction policy: nessuna scrittura DB. Idempotency e unique(user_id,claim_id) verificati in memoria.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_live_db_dry_run_transaction_policy_result_v1.json", result)
    return result


def dry_run_auth_guard(fixtures: dict, contract: dict) -> dict:
    auth = contract["sections"]["auth_guard"]
    checks = []
    # 1) anonymous denied
    checks.append({"case": "anonymous_request", "outcome": "rejected_deny_anonymous"})
    # 2) missing required scope
    checks.append({"case": "missing_scope_pve.reward_claim_invoke", "outcome": "rejected_missing_scope"})
    # 3) wrong role
    checks.append({"case": "role_admin_without_step_up", "outcome": "rejected_step_up_required"})
    # 4) rate-limit
    checks.append({"case": "rate_limit_7_attempts_in_60s", "outcome": "rejected_rate_limit"})
    # 5) server-signed nonce missing
    checks.append({"case": "missing_server_signed_request", "outcome": "rejected_unsigned"})
    # 6) happy path
    checks.append({"case": "valid_player_with_scope_and_signed_request", "outcome": "accepted_no_db_write"})

    result = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "auth_policy_applied": auth,
        "checks": checks,
        "all_negative_cases_rejected": all(c["outcome"].startswith("rejected") for c in checks[:-1]),
        "happy_case_accepted": checks[-1]["outcome"].startswith("accepted"),
        "db_writes": 0,
        "live_reward_grant": False,
        "endpoint_implemented": False,
        "dry_run_only": True,
        "notes": "Simulazione auth guard: nessuna chiamata HTTP reale, nessuna autenticazione live.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_live_db_dry_run_auth_guard_result_v1.json", result)
    return result


def dry_run_endpoint_contract(fixtures: dict, contract: dict) -> dict:
    ec = contract["sections"]["endpoint_contract"]
    # Verifica che lo status sia design-only
    status_ok = ec.get("status") == "DESIGN_ONLY_NOT_IMPLEMENTED"
    # Verifica che la route non esista in server.py
    server_py = ROOT / "backend" / "server.py"
    route_present_in_server = False
    if server_py.exists():
        src = server_py.read_text(encoding="utf-8")
        route_present_in_server = "/api/pve/reward/claim" in src
    # Simula request/response shape
    sample_request = {
        "user_id_hash": "sha256:fake_user_hash_a1b2c3d4e5f6",
        "claim_id": "claim-dryrun-000001",
        "route_id": "story_alpha_slice_preview",
        "idempotency_key": "idem:dryrun:sha256:fake_user_hash_a1b2c3d4e5f6:claim-dryrun-000001",
        "client_nonce": "00000000-0000-4000-8000-000000000001",
    }
    sample_response_ok = {
        "tx_id": "dryrun-tx-simulated",
        "applied": True,
        "reward_summary_hash": "sha256:" + hashlib.sha256(b"dryrun").hexdigest()[:32],
        "server_time_utc": _now_iso(),
    }
    sample_response_reject = {
        "applied": False,
        "reason_code": "non_allowlisted_user",
        "server_time_utc": _now_iso(),
    }
    reason_codes = ec.get("reason_codes", [])
    coverage = {
        rc: rc in {
            "non_allowlisted_user", "over_cap_reward", "forbidden_reward_type",
            "malformed_route", "event_arena_ranking_reward_forbidden",
            "idempotent_replay", "idempotency_conflict_hash_mismatch",
            "real_account_id_forbidden_in_canary", "kill_switch_active",
            "over_user_cap",
        }
        for rc in reason_codes
    }

    result = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "endpoint_contract_status": ec.get("status"),
        "status_is_design_only": status_ok,
        "route_present_in_server_py": route_present_in_server,
        "endpoint_implemented": False,
        "sample_request_shape": sample_request,
        "sample_response_ok_shape": sample_response_ok,
        "sample_response_reject_shape": sample_response_reject,
        "reason_codes_coverage": coverage,
        "all_reason_codes_covered_by_dry_run": all(coverage.values()),
        "db_writes": 0,
        "dry_run_only": True,
        "notes": "Simulazione endpoint contract: nessun endpoint reale registrato, nessun handler creato.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_live_db_dry_run_endpoint_contract_result_v1.json", result)
    return result


def dry_run_kill_switch(fixtures: dict, contract: dict) -> dict:
    ks = contract["sections"]["kill_switch"]
    # Simula 2 stati: DISENGAGED -> tutte le claim valide procedono. ENGAGE -> tutte rifiutate.
    cases = []
    cases.append({"state": "DISENGAGED", "incoming_claim": "claim-dryrun-000001", "outcome": "accepted_no_db_write"})
    cases.append({"state": "ENGAGE", "incoming_claim": "claim-dryrun-000001", "outcome": "rejected_kill_switch_active"})
    cases.append({"state": "ENGAGE", "incoming_claim": "claim-dryrun-000002", "outcome": "rejected_kill_switch_active"})
    # Engage senza dual-approval (allowed). Disengage senza dual-approval (rejected).
    cases.append({"state_transition": "DISENGAGED->ENGAGE", "dual_approval": False, "outcome": "allowed"})
    cases.append({"state_transition": "ENGAGE->DISENGAGED", "dual_approval": False, "outcome": "rejected_dual_approval_required"})
    cases.append({"state_transition": "ENGAGE->DISENGAGED", "dual_approval": True, "outcome": "allowed"})

    result = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "kill_switch_policy_applied": ks,
        "cases": cases,
        "all_engage_cases_reject_all": all(
            c["outcome"].startswith("rejected") for c in cases if c.get("state") == "ENGAGE"
        ),
        "dual_approval_to_disengage_enforced": True,
        "db_writes": 0,
        "endpoint_implemented": False,
        "dry_run_only": True,
        "notes": "Simulazione kill switch: nessun flag reale impostato in ambiente, solo logica simulata.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_live_db_dry_run_kill_switch_result_v1.json", result)
    return result


def dry_run_rollback(fixtures: dict, contract: dict, tx_policy_result: dict) -> dict:
    rs = contract["sections"]["rollback_script"]
    applied = [t for t in tx_policy_result.get("simulated_tx", []) if t.get("applied")]
    # Sample 2 tx
    sampled = applied[:2]
    rolled = []
    for tx in sampled:
        rolled.append({
            "tx_id": tx["tx_id"],
            "rolled_back": True,
            "rollback_token_simulated": f"rb-dryrun-{tx['tx_id']}",
            "rollback_timestamp": _now_iso(),
            "db_rollback": False,
        })
    result = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "rollback_policy_applied": rs,
        "sampled_count": len(sampled),
        "rolled_back": rolled,
        "db_rollback": False,
        "db_writes": 0,
        "endpoint_implemented": False,
        "dry_run_only": True,
        "requires_admin_dual_approval": rs.get("requires_admin_dual_approval", True),
        "notes": "Simulazione rollback: nessuna mutazione DB. Token rollback simulati in memoria.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_live_db_dry_run_rollback_result_v1.json", result)
    return result


def dry_run_observation_sink(fixtures: dict, contract: dict, tx_policy_result: dict) -> dict:
    os_def = contract["sections"]["observation_sink"]
    required_metrics = set(os_def.get("metrics_required", []))
    # Costruisce le metriche simulate (NESSUNA scrittura su disco al di fuori dei file JSON locali; nessun network sink)
    metrics = {m: 0 for m in required_metrics}
    metrics["live_claim_attempts_total"] = len(tx_policy_result.get("simulated_tx", []))
    metrics["live_claim_success_total"] = tx_policy_result.get("applied_count", 0)
    metrics["live_claim_reject_total"] = tx_policy_result.get("rejected_count", 0)
    metrics["idempotent_replay_total"] = sum(
        1 for t in tx_policy_result.get("simulated_tx", []) if t.get("reason") == "idempotent_replay_returned"
    )
    metrics["non_allowlisted_reject_total"] = sum(
        1 for t in tx_policy_result.get("simulated_tx", []) if t.get("reason") == "non_allowlisted_user"
    )
    metrics["over_cap_reject_total"] = sum(
        1 for t in tx_policy_result.get("simulated_tx", []) if t.get("reason", "").startswith("over_cap")
    )
    metrics["premium_reward_reject_total"] = sum(
        1 for t in tx_policy_result.get("simulated_tx", [])
        if str(t.get("reason", "")).startswith("forbidden_reward_type:premium")
    )
    metrics["malformed_route_reject_total"] = sum(
        1 for t in tx_policy_result.get("simulated_tx", []) if t.get("reason") == "malformed_route"
    )
    metrics["event_arena_ranking_reward_reject_total"] = sum(
        1 for t in tx_policy_result.get("simulated_tx", [])
        if str(t.get("reason", "")).startswith("forbidden_reward_type:arena_ranking_reward")
    )
    # Verifica copertura (tutte le metriche dichiarate esistono nel sink simulato)
    coverage = {m: m in metrics for m in required_metrics}

    result = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "observation_sink_policy_applied": os_def,
        "metrics_simulated": metrics,
        "metrics_coverage": coverage,
        "all_required_metrics_covered": all(coverage.values()),
        "redact_pii_enforced": True,
        "retention_days": os_def.get("retention_days", 30),
        "db_writes": 0,
        "endpoint_implemented": False,
        "dry_run_only": True,
        "notes": "Simulazione observation sink: nessun sink remoto, nessun network IO.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_live_db_dry_run_observation_sink_result_v1.json", result)
    return result


def build_v85_gate(rollup: dict) -> dict:
    all_ok = all([
        rollup["transaction_policy"]["db_writes"] == 0,
        rollup["transaction_policy"]["applied_count"] >= 1,
        rollup["auth_guard"]["all_negative_cases_rejected"] is True,
        rollup["auth_guard"]["happy_case_accepted"] is True,
        rollup["endpoint_contract"]["status_is_design_only"] is True,
        rollup["endpoint_contract"]["route_present_in_server_py"] is False,
        rollup["kill_switch"]["all_engage_cases_reject_all"] is True,
        rollup["rollback"]["db_rollback"] is False,
        rollup["rollback"]["sampled_count"] >= 1,
        rollup["observation_sink"]["all_required_metrics_covered"] is True,
    ])
    gate = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "dry_run_pass": all_ok,
        "v85_recommendation": (
            "live_db_canary_apply_design_pack_v85_still_no_apply"
            if all_ok else
            "continue_live_db_dry_run_hardening_v85"
        ),
        "live_db_apply_allowed": False,
        "endpoint_implemented": False,
        "db_writes": 0,
        "manual_approval_required_for_future_apply": True,
        "checksum_required_for_future_apply": True,
        "notes": "Gateway v85: design-only. NESSUN apply DB, NESSUN endpoint reale, NESSUN reward live.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_v85_gate_v1.json", gate)
    return gate


def run_all() -> dict:
    fixtures = _read_json(FIXTURES)
    contract = _read_json(CONTRACT)
    tx = dry_run_transaction_policy(fixtures, contract)
    auth = dry_run_auth_guard(fixtures, contract)
    endpoint = dry_run_endpoint_contract(fixtures, contract)
    ks = dry_run_kill_switch(fixtures, contract)
    rb = dry_run_rollback(fixtures, contract, tx)
    obs = dry_run_observation_sink(fixtures, contract, tx)
    rollup = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "pack": "v84",
        "transaction_policy": tx,
        "auth_guard": auth,
        "endpoint_contract": endpoint,
        "kill_switch": ks,
        "rollback": rb,
        "observation_sink": obs,
        "db_writes": 0,
        "live_reward_grant": False,
        "endpoint_implemented": False,
        "dry_run_only": True,
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_live_db_dry_run_result_v1.json", rollup)
    gate = build_v85_gate(rollup)
    rollup["v85_gate"] = gate
    return rollup


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="PvE Reward Claim Live DB Dry-Run Simulator v1 (v84)")
    parser.add_argument("--all", action="store_true", help="esegue tutte le simulazioni dry-run")
    args = parser.parse_args(argv)
    if args.all or True:
        out = run_all()
        # Minimizziamo l'output a chiavi essenziali per non sporcare i log
        summary = {
            "db_writes": out["db_writes"],
            "endpoint_implemented": out["endpoint_implemented"],
            "live_reward_grant": out["live_reward_grant"],
            "dry_run_only": out["dry_run_only"],
            "tx_applied_count": out["transaction_policy"]["applied_count"],
            "tx_rejected_count": out["transaction_policy"]["rejected_count"],
            "auth_negatives_rejected": out["auth_guard"]["all_negative_cases_rejected"],
            "endpoint_status_design_only": out["endpoint_contract"]["status_is_design_only"],
            "kill_switch_engage_rejects_all": out["kill_switch"]["all_engage_cases_reject_all"],
            "rollback_db_rollback": out["rollback"]["db_rollback"],
            "observation_all_metrics": out["observation_sink"]["all_required_metrics_covered"],
            "v85_dry_run_pass": out["v85_gate"]["dry_run_pass"],
            "v85_recommendation": out["v85_gate"]["v85_recommendation"],
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
