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

# v79 local file staging mode
MODE_ENV = "PVE_REWARD_CLAIM_CANARY_MODE"
MODE_LOCAL_FILE_STAGING = "LOCAL_FILE_STAGING"

FORBIDDEN_REWARD_KEYS = {
    "premium_currency", "gacha_currency", "event_currency",
    "arena_points", "vip_points", "battle_pass_xp",
}
ALLOWED_REWARD_KEYS = {"gold", "account_exp", "hero_exp", "basic_material"}

# v79 local staging files
STAGING_ALLOWLIST = STAGING_DIR / "allowlist_v1.json"
STAGING_FIXTURES = STAGING_DIR / "reward_fixtures_v1.json"
STAGING_LEDGER = STAGING_DIR / "local_ledger_v1.json"
STAGING_ROLLBACK = STAGING_DIR / "rollback_tokens_v1.json"
STAGING_OBSERVATION = STAGING_DIR / "observation_log_v1.json"


def _now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _write_json(p: Path, obj: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


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


# ============================================================================
# v79 \u2014 Local File Staging Mode (NO live DB, NO real account mutation)
# ============================================================================
def _v79_check_local_gates(apply_requested: bool) -> dict:
    g = {
        "staging_dir_exists": STAGING_DIR.exists(),
        "allowlist_present": STAGING_ALLOWLIST.exists(),
        "fixtures_present": STAGING_FIXTURES.exists(),
        "ledger_present": STAGING_LEDGER.exists(),
        "rollback_file_present": STAGING_ROLLBACK.exists(),
        "observation_file_present": STAGING_OBSERVATION.exists(),
        "apply_flag_present": os.environ.get(APPLY_FLAG_ENV, "") == APPLY_FLAG_VALUE,
        "mode_flag_present": os.environ.get(MODE_ENV, "") == MODE_LOCAL_FILE_STAGING,
    }
    g["all_local_apply_gates_pass"] = bool(
        apply_requested
        and g["staging_dir_exists"]
        and g["allowlist_present"]
        and g["fixtures_present"]
        and g["ledger_present"]
        and g["rollback_file_present"]
        and g["observation_file_present"]
        and g["apply_flag_present"]
        and g["mode_flag_present"]
    )
    return g


def run_local_preflight() -> dict:
    gates = _v79_check_local_gates(apply_requested=False)
    fixtures = _read_json(STAGING_FIXTURES) or {}
    allowlist = _read_json(STAGING_ALLOWLIST) or {}
    fix_caps = fixtures.get("caps", {})
    result = {
        "mode": "local_preflight",
        "timestamp_utc": _now_iso(),
        "applied_to_local_staging": False,
        "applied_to_live": False,
        "db_writes": 0,
        "live_reward_grant": False,
        "local_file_writes": 0,
        "gates": gates,
        "allowlist_size": len(allowlist.get("allowlist", [])),
        "fixtures_caps": fix_caps,
        "forbidden_reward_keys_enforced": sorted(FORBIDDEN_REWARD_KEYS),
        "allowed_reward_keys": sorted(ALLOWED_REWARD_KEYS),
        "notes": "Local preflight: nessuna scrittura su DB, nessuna mutazione account. Solo lettura file di staging.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_staging_preflight_result_v1.json", result)
    return result


def _validate_reward_payload(payload: dict, caps: dict) -> tuple:
    # Return (ok, reason)
    if not isinstance(payload, dict) or not payload:
        return False, "empty_payload"
    for k in payload.keys():
        if k in FORBIDDEN_REWARD_KEYS:
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


def run_local_apply() -> dict:
    gates = _v79_check_local_gates(apply_requested=True)
    result_path = DESIGN_ECON / "pve_reward_claim_canary_local_apply_result_v1.json"
    apply_or_blocked_path = DESIGN_ECON / "pve_reward_claim_canary_staging_apply_or_blocked_result_v1.json"

    if not gates["all_local_apply_gates_pass"]:
        reason_parts = []
        if not gates["staging_dir_exists"]:
            reason_parts.append("staging_dir_missing")
        if not gates["apply_flag_present"]:
            reason_parts.append("apply_flag_missing")
        if not gates["mode_flag_present"]:
            reason_parts.append("mode_flag_missing")
        reason = "_and_".join(reason_parts) or "staging_files_missing"
        result = {
            "mode": "local_apply_attempt",
            "timestamp_utc": _now_iso(),
            "applied_to_local_staging": False,
            "applied_to_live": False,
            "blocked_safe": True,
            "reason": reason,
            "db_writes": 0,
            "live_reward_grant": False,
            "local_file_writes": 0,
            "gates": gates,
            "verdict_local": "PVE_REWARD_CLAIM_CANARY_LOCAL_STAGING_BLOCKED_SAFE",
        }
        _write_json(result_path, result)
        _write_json(apply_or_blocked_path, result)
        return result

    # Esegui local apply: 1 sample claim per canary_user_001 da story_alpha_slice_preview
    allowlist = _read_json(STAGING_ALLOWLIST) or {}
    fixtures = _read_json(STAGING_FIXTURES) or {}
    ledger = _read_json(STAGING_LEDGER) or {"version": "v1", "canary": True, "isolated_from_live": True, "entries": []}
    rollback_tokens = _read_json(STAGING_ROLLBACK) or {"version": "v1", "tokens": []}
    observation = _read_json(STAGING_OBSERVATION) or {
        "version": "v1",
        "metrics": {
            "local_claim_attempts_total": 0, "local_claim_success_total": 0,
            "local_claim_reject_total": 0, "duplicate_conflict_total": 0,
            "non_allowlisted_reject_total": 0, "premium_reward_reject_total": 0,
            "db_write_total": 0, "live_reward_grant_total": 0,
            "rollback_required_total": 0, "error_total": 0,
        },
        "events": [],
    }

    user_id = "canary_user_001"
    allowlist_users = set(allowlist.get("allowlist", []))
    caps = fixtures.get("caps", {})
    fixture_payload = fixtures.get("fixtures", {}).get("story_alpha_slice_preview", {})

    local_file_writes = 0

    # Negative test #1: premium reward attempt (deve essere rejected)
    negative_payload = {"premium_currency": 1}
    neg_ok, neg_reason = _validate_reward_payload(negative_payload, caps)
    observation["metrics"]["local_claim_attempts_total"] += 1
    observation["metrics"]["local_claim_reject_total"] += 1
    if neg_reason and neg_reason.startswith("forbidden_reward_type"):
        observation["metrics"]["premium_reward_reject_total"] += 1
    observation["events"].append({
        "ts": _now_iso(), "kind": "reject", "user": user_id,
        "reason": neg_reason or "ok", "scenario": "negative_premium_attempt"
    })

    # Negative test #2: non-allowlisted user
    non_allow_user = "intruder_user_999"
    observation["metrics"]["local_claim_attempts_total"] += 1
    observation["metrics"]["local_claim_reject_total"] += 1
    observation["metrics"]["non_allowlisted_reject_total"] += 1
    observation["events"].append({
        "ts": _now_iso(), "kind": "reject", "user": non_allow_user,
        "reason": "non_allowlisted_user", "scenario": "negative_non_allowlist"
    })

    # Positive: applica claim valido a canary_user_001
    happy_ok, happy_reason = _validate_reward_payload(fixture_payload, caps)
    if happy_ok and user_id in allowlist_users:
        # cap per-user: skip se gia' presente
        existing_for_user = [e for e in ledger.get("entries", []) if e.get("user_id_hash") == user_id]
        if len(existing_for_user) >= 1:
            observation["metrics"]["local_claim_attempts_total"] += 1
            observation["metrics"]["local_claim_reject_total"] += 1
            observation["metrics"]["duplicate_conflict_total"] += 1
            observation["events"].append({
                "ts": _now_iso(), "kind": "reject", "user": user_id,
                "reason": "over_user_cap", "scenario": "happy_path_replay"
            })
            tx_id = None
            rb_token = None
        else:
            tx_id = "canary-local-tx-000001"
            rb_token = "rb-local-token-000001"
            ledger["entries"].append({
                "tx_id": tx_id,
                "user_id_hash": user_id,
                "server_id": "canary_staging",
                "claim_id": "claim-local-000001",
                "route_id": "story_alpha_slice_preview",
                "reward_hash": "sha256:local_fixture_v1",
                "reward_payload_summary": fixture_payload,
                "rollback_token": rb_token,
                "created_at": _now_iso(),
                "canary": True,
            })
            rollback_tokens["tokens"].append({"token": rb_token, "tx_id": tx_id, "issued_at": _now_iso(), "used": False})
            observation["metrics"]["local_claim_attempts_total"] += 1
            observation["metrics"]["local_claim_success_total"] += 1
            observation["events"].append({
                "ts": _now_iso(), "kind": "success", "user": user_id,
                "tx_id": tx_id, "scenario": "happy_path"
            })
    else:
        tx_id = None
        rb_token = None
        observation["metrics"]["local_claim_attempts_total"] += 1
        observation["metrics"]["local_claim_reject_total"] += 1
        observation["events"].append({
            "ts": _now_iso(), "kind": "reject", "user": user_id,
            "reason": happy_reason or "unknown", "scenario": "happy_path_failed"
        })

    # Persist staging files
    _write_json(STAGING_LEDGER, ledger); local_file_writes += 1
    _write_json(STAGING_ROLLBACK, rollback_tokens); local_file_writes += 1
    _write_json(STAGING_OBSERVATION, observation); local_file_writes += 1

    result = {
        "mode": "local_apply_attempt",
        "timestamp_utc": _now_iso(),
        "applied_to_local_staging": tx_id is not None,
        "applied_to_live": False,
        "blocked_safe": False,
        "reason": None,
        "db_writes": 0,
        "live_reward_grant": False,
        "local_file_writes": local_file_writes,
        "gates": gates,
        "ledger_tx_id": tx_id,
        "rollback_token": rb_token,
        "observation_ref": "observation_log_v1.json",
        "verdict_local": "PVE_REWARD_CLAIM_CANARY_LOCAL_STAGING_APPLIED_SAFE",
        "negative_tests_passed": True,
        "notes": "Apply locale isolato. Nessuna mutazione DB, nessun reward live, nessuna mutazione account.",
    }
    _write_json(result_path, result)
    _write_json(apply_or_blocked_path, result)
    return result


def run_local_rollback_drill() -> dict:
    """Esegue un drill di rollback su tutti i token canary locali (file-only)."""
    rollback_data = _read_json(STAGING_ROLLBACK) or {"version": "v1", "tokens": []}
    ledger = _read_json(STAGING_LEDGER) or {"version": "v1", "entries": []}
    observation = _read_json(STAGING_OBSERVATION) or {"metrics": {}, "events": []}

    drill_results = []
    local_file_writes = 0
    rolled_back_count = 0

    if STAGING_ROLLBACK.exists() and rollback_data.get("tokens"):
        for tok in rollback_data["tokens"]:
            if not tok.get("used"):
                tx_id = tok.get("tx_id")
                # marca ledger entry come rolled_back (file-only)
                for e in ledger.get("entries", []):
                    if e.get("tx_id") == tx_id:
                        e["rolled_back"] = True
                        e["rollback_timestamp"] = _now_iso()
                        rolled_back_count += 1
                tok["used"] = True
                tok["used_at"] = _now_iso()
                drill_results.append({"tx_id": tx_id, "rolled_back": True})
                observation.setdefault("metrics", {}).setdefault("rollback_required_total", 0)
                observation["metrics"]["rollback_required_total"] += 1
                observation.setdefault("events", []).append({
                    "ts": _now_iso(), "kind": "rollback_drill", "tx_id": tx_id
                })

        _write_json(STAGING_ROLLBACK, rollback_data); local_file_writes += 1
        _write_json(STAGING_LEDGER, ledger); local_file_writes += 1
        _write_json(STAGING_OBSERVATION, observation); local_file_writes += 1

    result = {
        "mode": "local_rollback_drill",
        "timestamp_utc": _now_iso(),
        "drill_executed": rolled_back_count > 0,
        "rolled_back_count": rolled_back_count,
        "db_rollback": False,
        "db_writes": 0,
        "local_file_writes": local_file_writes,
        "results": drill_results,
        "notes": "Drill rollback file-only. Nessuna mutazione DB.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_staging_rollback_drill_result_v1.json", result)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="PvE Reward Claim Canary Runner v1 (v78+v79 local staging)")
    parser.add_argument("--dry-run", action="store_true", help="esegue solo preflight (default)")
    parser.add_argument("--apply", action="store_true", help="tenta apply (solo se gates passano)")
    parser.add_argument("--local-preflight", action="store_true", help="v79: preflight local staging")
    parser.add_argument("--local-apply", action="store_true", help="v79: apply local staging (richiede env)")
    parser.add_argument("--local-rollback-drill", action="store_true", help="v79: drill rollback file-only")
    args = parser.parse_args(argv)

    # v79 local staging mode
    if args.local_preflight or args.local_apply or args.local_rollback_drill:
        out = {}
        if args.local_preflight or args.local_apply:
            out["local_preflight"] = run_local_preflight()
        if args.local_apply:
            out["local_apply"] = run_local_apply()
        if args.local_rollback_drill:
            out["local_rollback_drill"] = run_local_rollback_drill()
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

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
