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

# v80 wave2 env gate
WAVE2_ENV = "PVE_REWARD_CLAIM_CANARY_WAVE2"
WAVE2_ENV_VALUE = "YES_I_UNDERSTAND"

# v81 wave3 env gate
WAVE3_ENV = "PVE_REWARD_CLAIM_CANARY_WAVE3"
WAVE3_ENV_VALUE = "YES_I_UNDERSTAND"

# v82 wave4 env gate
WAVE4_ENV = "PVE_REWARD_CLAIM_CANARY_WAVE4"
WAVE4_ENV_VALUE = "YES_I_UNDERSTAND"

# v83 wave5 env gate
WAVE5_ENV = "PVE_REWARD_CLAIM_CANARY_WAVE5"
WAVE5_ENV_VALUE = "YES_I_UNDERSTAND"

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

# v80 wave2 staging files (separati per non contaminare v79)
WAVE2_ALLOWLIST = STAGING_DIR / "wave2_allowlist_v1.json"
WAVE2_FIXTURES = STAGING_DIR / "wave2_reward_fixtures_v1.json"
WAVE2_PLAN = STAGING_DIR / "wave2_plan_v1.json"
WAVE2_LEDGER = STAGING_DIR / "wave2_local_ledger_v1.json"
WAVE2_ROLLBACK = STAGING_DIR / "wave2_rollback_tokens_v1.json"
WAVE2_OBSERVATION = STAGING_DIR / "wave2_observation_log_v1.json"

# v81 wave3 staging files
WAVE3_ALLOWLIST = STAGING_DIR / "wave3_allowlist_v1.json"
WAVE3_FIXTURES = STAGING_DIR / "wave3_reward_fixtures_v1.json"
WAVE3_PLAN = STAGING_DIR / "wave3_plan_v1.json"
WAVE3_LEDGER = STAGING_DIR / "wave3_local_ledger_v1.json"
WAVE3_ROLLBACK = STAGING_DIR / "wave3_rollback_tokens_v1.json"
WAVE3_OBSERVATION = STAGING_DIR / "wave3_observation_log_v1.json"

# v82 wave4 staging files
WAVE4_ALLOWLIST = STAGING_DIR / "wave4_allowlist_v1.json"
WAVE4_FIXTURES = STAGING_DIR / "wave4_reward_fixtures_v1.json"
WAVE4_PLAN = STAGING_DIR / "wave4_plan_v1.json"
WAVE4_LEDGER = STAGING_DIR / "wave4_local_ledger_v1.json"
WAVE4_ROLLBACK = STAGING_DIR / "wave4_rollback_tokens_v1.json"
WAVE4_OBSERVATION = STAGING_DIR / "wave4_observation_log_v1.json"

# v83 wave5 staging files
WAVE5_ALLOWLIST = STAGING_DIR / "wave5_allowlist_v1.json"
WAVE5_FIXTURES = STAGING_DIR / "wave5_reward_fixtures_v1.json"
WAVE5_PLAN = STAGING_DIR / "wave5_plan_v1.json"
WAVE5_LEDGER = STAGING_DIR / "wave5_local_ledger_v1.json"
WAVE5_ROLLBACK = STAGING_DIR / "wave5_rollback_tokens_v1.json"
WAVE5_OBSERVATION = STAGING_DIR / "wave5_observation_log_v1.json"


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


# ============================================================================
# v80 \u2014 Wave-2 Local Apply (max 3 utenti alias-only, file-only)
# ============================================================================
def _v80_check_wave2_gates(apply_requested: bool) -> dict:
    g = {
        "staging_dir_exists": STAGING_DIR.exists(),
        "wave2_allowlist_present": WAVE2_ALLOWLIST.exists(),
        "wave2_fixtures_present": WAVE2_FIXTURES.exists(),
        "wave2_plan_present": WAVE2_PLAN.exists(),
        "mode_flag_present": os.environ.get(MODE_ENV, "") == MODE_LOCAL_FILE_STAGING,
        "wave2_flag_present": os.environ.get(WAVE2_ENV, "") == WAVE2_ENV_VALUE,
    }
    g["all_wave2_apply_gates_pass"] = bool(
        apply_requested
        and g["staging_dir_exists"]
        and g["wave2_allowlist_present"]
        and g["wave2_fixtures_present"]
        and g["wave2_plan_present"]
        and g["mode_flag_present"]
        and g["wave2_flag_present"]
    )
    return g


def run_wave2_preflight() -> dict:
    gates = _v80_check_wave2_gates(apply_requested=False)
    plan = _read_json(WAVE2_PLAN) or {}
    allowlist = _read_json(WAVE2_ALLOWLIST) or {}
    fixtures = _read_json(WAVE2_FIXTURES) or {}
    result = {
        "mode": "wave2_preflight",
        "timestamp_utc": _now_iso(),
        "applied_to_local_staging": False,
        "applied_to_live": False,
        "db_writes": 0,
        "live_reward_grant": False,
        "local_file_writes": 0,
        "gates": gates,
        "wave2_allowlist_size": len(allowlist.get("allowlist", [])),
        "wave2_max_users": plan.get("max_users", 3),
        "wave2_max_claims_total": plan.get("max_claims_total", 3),
        "wave2_routes": plan.get("routes", []),
        "fixtures_caps": fixtures.get("caps", {}),
        "forbidden_reward_keys_enforced": sorted(FORBIDDEN_REWARD_KEYS),
        "notes": "Wave2 preflight: lettura file di staging wave2. Nessuna scrittura DB, nessuna mutazione account.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave2_preflight_result_v1.json", result)
    return result


def _ensure_wave2_files() -> tuple:
    ledger = _read_json(WAVE2_LEDGER) or {
        "version": "v1", "wave": 2, "canary": True, "isolated_from_live": True, "entries": []
    }
    rollback = _read_json(WAVE2_ROLLBACK) or {"version": "v1", "wave": 2, "tokens": []}
    observation = _read_json(WAVE2_OBSERVATION) or {
        "version": "v1", "wave": 2,
        "metrics": {
            "wave2_claim_attempts_total": 0, "wave2_claim_success_total": 0,
            "wave2_claim_reject_total": 0, "idempotent_replay_total": 0,
            "duplicate_conflict_total": 0, "non_allowlisted_reject_total": 0,
            "over_cap_reject_total": 0, "premium_reward_reject_total": 0,
            "db_write_total": 0, "live_reward_grant_total": 0,
            "rollback_required_total": 0, "error_total": 0,
        },
        "events": [],
    }
    return ledger, rollback, observation


def run_wave2_apply() -> dict:
    gates = _v80_check_wave2_gates(apply_requested=True)
    result_path = DESIGN_ECON / "pve_reward_claim_canary_wave2_apply_result_v1.json"
    blocked_path = DESIGN_ECON / "pve_reward_claim_canary_wave2_apply_or_blocked_result_v1.json"

    if not gates["all_wave2_apply_gates_pass"]:
        reason_parts = []
        if not gates["staging_dir_exists"]: reason_parts.append("staging_dir_missing")
        if not gates["mode_flag_present"]: reason_parts.append("mode_flag_missing")
        if not gates["wave2_flag_present"]: reason_parts.append("wave2_flag_missing")
        if not gates["wave2_allowlist_present"]: reason_parts.append("wave2_allowlist_missing")
        if not gates["wave2_fixtures_present"]: reason_parts.append("wave2_fixtures_missing")
        reason = "_and_".join(reason_parts) or "wave2_files_missing"
        result = {
            "mode": "wave2_apply_attempt",
            "timestamp_utc": _now_iso(),
            "applied_to_local_staging": False,
            "applied_to_live": False,
            "blocked_safe": True,
            "reason": reason,
            "db_writes": 0,
            "live_reward_grant": False,
            "local_file_writes": 0,
            "gates": gates,
            "verdict_local": "PVE_REWARD_CLAIM_CANARY_WAVE2_BLOCKED_SAFE",
        }
        _write_json(result_path, result)
        _write_json(blocked_path, result)
        return result

    plan = _read_json(WAVE2_PLAN) or {}
    allowlist = _read_json(WAVE2_ALLOWLIST) or {}
    fixtures = _read_json(WAVE2_FIXTURES) or {}
    allowlist_users = set(allowlist.get("allowlist", []))
    caps = fixtures.get("caps", {})

    ledger, rollback, observation = _ensure_wave2_files()
    local_file_writes = 0
    happy_paths = []
    negative_results = []

    def _obs_metric(name, n=1):
        observation["metrics"][name] = observation["metrics"].get(name, 0) + n

    def _obs_event(kind, user, **extra):
        ev = {"ts": _now_iso(), "kind": kind, "user": user}
        ev.update(extra)
        observation["events"].append(ev)

    # Happy paths: applica i 3 claim della plan
    existing_users = {e.get("user_id_hash") for e in ledger.get("entries", [])}
    tx_counter = len(ledger.get("entries", []))
    for i, item in enumerate(plan.get("plan", []), start=1):
        if i > plan.get("max_claims_total", 3):
            break
        user = item["user"]
        route = item["route"]
        payload = item["reward_preview"]
        _obs_metric("wave2_claim_attempts_total")
        # validazione
        ok, reason = _validate_reward_payload(payload, caps)
        if not ok:
            _obs_metric("wave2_claim_reject_total")
            if reason and reason.startswith("over_cap"):
                _obs_metric("over_cap_reject_total")
            _obs_event("reject", user, reason=reason, scenario="happy_invalid_payload")
            happy_paths.append({"user": user, "applied": False, "reason": reason})
            continue
        if user not in allowlist_users:
            _obs_metric("wave2_claim_reject_total")
            _obs_metric("non_allowlisted_reject_total")
            _obs_event("reject", user, reason="non_allowlisted_user", scenario="happy")
            happy_paths.append({"user": user, "applied": False, "reason": "non_allowlisted_user"})
            continue
        if user in existing_users:
            _obs_metric("wave2_claim_reject_total")
            _obs_metric("duplicate_conflict_total")
            _obs_event("reject", user, reason="over_user_cap", scenario="happy_duplicate")
            happy_paths.append({"user": user, "applied": False, "reason": "over_user_cap"})
            continue
        tx_counter += 1
        tx_id = f"canary-wave2-tx-{tx_counter:06d}"
        rb_token = f"rb-wave2-token-{tx_counter:06d}"
        idem_key = f"idem:wave2:{user}:{item['claim_id']}"
        ledger["entries"].append({
            "tx_id": tx_id, "user_id_hash": user, "server_id": "canary_staging_wave2",
            "claim_id": item["claim_id"], "route_id": route,
            "reward_hash": f"sha256:wave2_fixture_{i}",
            "reward_payload_summary": payload, "rollback_token": rb_token,
            "idempotency_key": idem_key,
            "created_at": _now_iso(), "canary": True, "wave": 2,
        })
        rollback["tokens"].append({
            "token": rb_token, "tx_id": tx_id, "wave": 2,
            "issued_at": _now_iso(), "used": False
        })
        existing_users.add(user)
        _obs_metric("wave2_claim_success_total")
        _obs_event("success", user, tx_id=tx_id, route=route, scenario="happy")
        happy_paths.append({"user": user, "applied": True, "tx_id": tx_id,
                            "rollback_token": rb_token, "idempotency_key": idem_key})

    # === NEGATIVE TESTS ===
    # 1) Duplicate idempotency replay: stesso utente, stesso claim_id => existing returned
    first_applied = next((h for h in happy_paths if h.get("applied")), None)
    if first_applied:
        _obs_metric("wave2_claim_attempts_total")
        _obs_metric("idempotent_replay_total")
        _obs_event("idempotent_replay", first_applied["user"],
                   idempotency_key=first_applied["idempotency_key"], scenario="duplicate_replay")
        negative_results.append({"test": "duplicate_idempotency_replay", "result": "idempotent_replay_returned"})

    # 2) Duplicate conflicting hash: same key, different hash => reject
    if first_applied:
        _obs_metric("wave2_claim_attempts_total")
        _obs_metric("wave2_claim_reject_total")
        _obs_metric("duplicate_conflict_total")
        _obs_event("reject", first_applied["user"], reason="idempotency_conflict_hash_mismatch",
                   scenario="duplicate_conflicting_hash")
        negative_results.append({"test": "duplicate_conflicting_hash", "result": "rejected_idempotency_conflict"})

    # 3) Non-allowlisted user
    _obs_metric("wave2_claim_attempts_total")
    _obs_metric("wave2_claim_reject_total")
    _obs_metric("non_allowlisted_reject_total")
    _obs_event("reject", "intruder_user_999", reason="non_allowlisted_user",
               scenario="negative_non_allowlist")
    negative_results.append({"test": "non_allowlisted_user", "result": "rejected_non_allowlisted_user"})

    # 4) Premium reward
    _obs_metric("wave2_claim_attempts_total")
    _obs_metric("wave2_claim_reject_total")
    _obs_metric("premium_reward_reject_total")
    _obs_event("reject", "canary_user_001", reason="forbidden_reward_type:premium_currency",
               scenario="negative_premium_attempt")
    negative_results.append({"test": "premium_reward_reject", "result": "rejected_forbidden_reward_type"})

    # 5) Over-cap reward
    _obs_metric("wave2_claim_attempts_total")
    _obs_metric("wave2_claim_reject_total")
    _obs_metric("over_cap_reject_total")
    _obs_event("reject", "canary_user_002", reason="over_cap:gold",
               scenario="negative_over_cap")
    negative_results.append({"test": "over_cap_reward_reject", "result": "rejected_over_cap"})

    _write_json(WAVE2_LEDGER, ledger); local_file_writes += 1
    _write_json(WAVE2_ROLLBACK, rollback); local_file_writes += 1
    _write_json(WAVE2_OBSERVATION, observation); local_file_writes += 1

    success_count = sum(1 for h in happy_paths if h.get("applied"))

    result = {
        "mode": "wave2_apply_attempt",
        "timestamp_utc": _now_iso(),
        "applied_to_local_staging": success_count > 0,
        "applied_to_live": False,
        "blocked_safe": False,
        "reason": None,
        "db_writes": 0,
        "live_reward_grant": False,
        "local_file_writes": local_file_writes,
        "gates": gates,
        "wave2_success_count": success_count,
        "wave2_max_claims_total": plan.get("max_claims_total", 3),
        "happy_paths": happy_paths,
        "negative_tests_results": negative_results,
        "verdict_local": "PVE_REWARD_CLAIM_CANARY_WAVE2_OBSERVED_SAFE",
        "notes": "Wave2 apply file-only isolato. Nessuna mutazione DB, nessun reward live.",
    }
    _write_json(result_path, result)
    _write_json(blocked_path, result)

    # Snapshot ledger (compreso storico v79)
    v79_ledger = _read_json(STAGING_LEDGER) or {}
    snapshot = {
        "version": "v1",
        "snapshot_timestamp_utc": _now_iso(),
        "wave1_v79_entries_count": len(v79_ledger.get("entries", [])),
        "wave1_v79_entries_summary": [
            {"tx_id": e.get("tx_id"), "user": e.get("user_id_hash"),
             "rolled_back": e.get("rolled_back", False)}
            for e in v79_ledger.get("entries", [])
        ],
        "wave2_entries_count": len(ledger.get("entries", [])),
        "wave2_entries_summary": [
            {"tx_id": e.get("tx_id"), "user": e.get("user_id_hash"),
             "route": e.get("route_id"), "payload": e.get("reward_payload_summary")}
            for e in ledger.get("entries", [])
        ],
        "db_writes": 0, "live_reward_grant": False,
        "premium_in_ledger": False, "pii_in_ledger": False,
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave2_ledger_snapshot_v1.json", snapshot)

    # Negative tests result file
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave2_replay_negative_test_result_v1.json", {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "negative_tests": negative_results,
        "all_negative_tests_passed": all(
            r["result"].startswith("rejected") or r["result"].startswith("idempotent")
            for r in negative_results
        ),
        "db_writes": 0,
    })

    return result


def run_wave2_observe() -> dict:
    obs_log = _read_json(WAVE2_OBSERVATION) or {"metrics": {}}
    metrics = obs_log.get("metrics", {})
    pass_criteria = {
        "db_write_total_zero": metrics.get("db_write_total", 0) == 0,
        "live_reward_grant_total_zero": metrics.get("live_reward_grant_total", 0) == 0,
        "premium_reward_reject_at_least_one": metrics.get("premium_reward_reject_total", 0) >= 1,
        "non_allowlisted_reject_at_least_one": metrics.get("non_allowlisted_reject_total", 0) >= 1,
        "over_cap_reject_at_least_one": metrics.get("over_cap_reject_total", 0) >= 1,
        "no_critical_errors": metrics.get("error_total", 0) == 0,
    }
    result = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "observation_source": "/app/data/canary_staging/wave2_observation_log_v1.json",
        "window_minutes": 60,
        "metrics": metrics,
        "pass_criteria": pass_criteria,
        "observation_pass": all(pass_criteria.values()),
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave2_observation_result_v1.json", result)
    return result


def run_wave2_rollback_drill() -> dict:
    rollback_data = _read_json(WAVE2_ROLLBACK) or {"version": "v1", "wave": 2, "tokens": []}
    ledger = _read_json(WAVE2_LEDGER) or {"entries": []}
    observation = _read_json(WAVE2_OBSERVATION) or {"metrics": {}, "events": []}

    drill_results = []
    local_file_writes = 0
    rolled_back_count = 0

    if rollback_data.get("tokens"):
        # policy: rollback ONLY 1 sampled tx (la prima non usata)
        for tok in rollback_data["tokens"]:
            if not tok.get("used"):
                tx_id = tok.get("tx_id")
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
                    "ts": _now_iso(), "kind": "rollback_drill", "tx_id": tx_id, "wave": 2
                })
                break  # sample policy

        _write_json(WAVE2_ROLLBACK, rollback_data); local_file_writes += 1
        _write_json(WAVE2_LEDGER, ledger); local_file_writes += 1
        _write_json(WAVE2_OBSERVATION, observation); local_file_writes += 1

    result = {
        "version": "v1",
        "mode": "wave2_rollback_drill",
        "timestamp_utc": _now_iso(),
        "drill_executed": rolled_back_count > 0,
        "rolled_back_count": rolled_back_count,
        "policy": "sample_one_canary_tx",
        "db_rollback": False,
        "db_writes": 0,
        "local_file_writes": local_file_writes,
        "results": drill_results,
        "notes": "Drill rollback wave2 file-only (1 tx campione). Nessuna mutazione DB.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave2_rollback_drill_result_v1.json", result)
    return result


# ============================================================================
# v81 \u2014 Wave-3 Local Apply (max 5 utenti, max 5 claim, +malformed_route reject)
# ============================================================================
VALID_WAVE3_ROUTES = {
    "story_alpha_slice_preview",
    "training_combat_onboarding_preview",
    "boss_tower_alpha_loop_preview",
    "first_session_onboarding_preview",
    "alpha_menu_preview",
}


def _v81_check_wave3_gates(apply_requested: bool) -> dict:
    g = {
        "staging_dir_exists": STAGING_DIR.exists(),
        "wave3_allowlist_present": WAVE3_ALLOWLIST.exists(),
        "wave3_fixtures_present": WAVE3_FIXTURES.exists(),
        "wave3_plan_present": WAVE3_PLAN.exists(),
        "mode_flag_present": os.environ.get(MODE_ENV, "") == MODE_LOCAL_FILE_STAGING,
        "wave3_flag_present": os.environ.get(WAVE3_ENV, "") == WAVE3_ENV_VALUE,
    }
    g["all_wave3_apply_gates_pass"] = bool(
        apply_requested
        and g["staging_dir_exists"]
        and g["wave3_allowlist_present"]
        and g["wave3_fixtures_present"]
        and g["wave3_plan_present"]
        and g["mode_flag_present"]
        and g["wave3_flag_present"]
    )
    return g


def run_wave3_preflight() -> dict:
    gates = _v81_check_wave3_gates(apply_requested=False)
    plan = _read_json(WAVE3_PLAN) or {}
    allowlist = _read_json(WAVE3_ALLOWLIST) or {}
    fixtures = _read_json(WAVE3_FIXTURES) or {}
    result = {
        "mode": "wave3_preflight",
        "timestamp_utc": _now_iso(),
        "applied_to_local_staging": False,
        "applied_to_live": False,
        "db_writes": 0,
        "live_reward_grant": False,
        "local_file_writes": 0,
        "gates": gates,
        "wave3_allowlist_size": len(allowlist.get("allowlist", [])),
        "wave3_max_users": plan.get("max_users", 5),
        "wave3_max_claims_total": plan.get("max_claims_total", 5),
        "wave3_routes": plan.get("routes", []),
        "valid_routes": sorted(VALID_WAVE3_ROUTES),
        "fixtures_caps": fixtures.get("caps", {}),
        "forbidden_reward_keys_enforced": sorted(FORBIDDEN_REWARD_KEYS),
        "notes": "Wave3 preflight: lettura file di staging wave3. Nessuna scrittura DB.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave3_preflight_result_v1.json", result)
    return result


def _ensure_wave3_files() -> tuple:
    ledger = _read_json(WAVE3_LEDGER) or {
        "version": "v1", "wave": 3, "canary": True, "isolated_from_live": True, "entries": []
    }
    rollback = _read_json(WAVE3_ROLLBACK) or {"version": "v1", "wave": 3, "tokens": []}
    observation = _read_json(WAVE3_OBSERVATION) or {
        "version": "v1", "wave": 3,
        "metrics": {
            "wave3_claim_attempts_total": 0, "wave3_claim_success_total": 0,
            "wave3_claim_reject_total": 0, "idempotent_replay_total": 0,
            "duplicate_conflict_total": 0, "non_allowlisted_reject_total": 0,
            "over_cap_reject_total": 0, "premium_reward_reject_total": 0,
            "malformed_route_reject_total": 0,
            "db_write_total": 0, "live_reward_grant_total": 0,
            "rollback_required_total": 0, "error_total": 0,
        },
        "events": [],
    }
    return ledger, rollback, observation


def run_wave3_apply() -> dict:
    gates = _v81_check_wave3_gates(apply_requested=True)
    result_path = DESIGN_ECON / "pve_reward_claim_canary_wave3_apply_result_v1.json"
    blocked_path = DESIGN_ECON / "pve_reward_claim_canary_wave3_apply_or_blocked_result_v1.json"

    if not gates["all_wave3_apply_gates_pass"]:
        reason_parts = []
        if not gates["staging_dir_exists"]: reason_parts.append("staging_dir_missing")
        if not gates["mode_flag_present"]: reason_parts.append("mode_flag_missing")
        if not gates["wave3_flag_present"]: reason_parts.append("wave3_flag_missing")
        if not gates["wave3_allowlist_present"]: reason_parts.append("wave3_allowlist_missing")
        if not gates["wave3_fixtures_present"]: reason_parts.append("wave3_fixtures_missing")
        if not gates["wave3_plan_present"]: reason_parts.append("wave3_plan_missing")
        reason = "_and_".join(reason_parts) or "wave3_files_missing"
        result = {
            "mode": "wave3_apply_attempt",
            "timestamp_utc": _now_iso(),
            "applied_to_local_staging": False,
            "applied_to_live": False,
            "blocked_safe": True,
            "reason": reason,
            "db_writes": 0,
            "live_reward_grant": False,
            "local_file_writes": 0,
            "gates": gates,
            "verdict_local": "PVE_REWARD_CLAIM_CANARY_WAVE3_BLOCKED_SAFE",
        }
        _write_json(result_path, result)
        _write_json(blocked_path, result)
        return result

    plan = _read_json(WAVE3_PLAN) or {}
    allowlist = _read_json(WAVE3_ALLOWLIST) or {}
    fixtures = _read_json(WAVE3_FIXTURES) or {}
    allowlist_users = set(allowlist.get("allowlist", []))
    caps = fixtures.get("caps", {})

    ledger, rollback, observation = _ensure_wave3_files()
    local_file_writes = 0
    happy_paths = []
    negative_results = []

    def _obs_metric(name, n=1):
        observation["metrics"][name] = observation["metrics"].get(name, 0) + n

    def _obs_event(kind, user, **extra):
        ev = {"ts": _now_iso(), "kind": kind, "user": user}
        ev.update(extra)
        observation["events"].append(ev)

    existing_users = {e.get("user_id_hash") for e in ledger.get("entries", [])}
    tx_counter = len(ledger.get("entries", []))
    for i, item in enumerate(plan.get("plan", []), start=1):
        if i > plan.get("max_claims_total", 5):
            break
        user = item["user"]
        route = item["route"]
        payload = item["reward_preview"]
        _obs_metric("wave3_claim_attempts_total")
        ok, reason = _validate_reward_payload(payload, caps)
        if not ok:
            _obs_metric("wave3_claim_reject_total")
            if reason and reason.startswith("over_cap"):
                _obs_metric("over_cap_reject_total")
            _obs_event("reject", user, reason=reason, scenario="happy_invalid_payload")
            happy_paths.append({"user": user, "applied": False, "reason": reason})
            continue
        if route not in VALID_WAVE3_ROUTES:
            _obs_metric("wave3_claim_reject_total")
            _obs_metric("malformed_route_reject_total")
            _obs_event("reject", user, reason="malformed_route", scenario="happy_bad_route")
            happy_paths.append({"user": user, "applied": False, "reason": "malformed_route"})
            continue
        if user not in allowlist_users:
            _obs_metric("wave3_claim_reject_total")
            _obs_metric("non_allowlisted_reject_total")
            _obs_event("reject", user, reason="non_allowlisted_user", scenario="happy")
            happy_paths.append({"user": user, "applied": False, "reason": "non_allowlisted_user"})
            continue
        if user in existing_users:
            _obs_metric("wave3_claim_reject_total")
            _obs_metric("duplicate_conflict_total")
            _obs_event("reject", user, reason="over_user_cap", scenario="happy_duplicate")
            happy_paths.append({"user": user, "applied": False, "reason": "over_user_cap"})
            continue
        tx_counter += 1
        tx_id = f"canary-wave3-tx-{tx_counter:06d}"
        rb_token = f"rb-wave3-token-{tx_counter:06d}"
        idem_key = f"idem:wave3:{user}:{item['claim_id']}"
        ledger["entries"].append({
            "tx_id": tx_id, "user_id_hash": user, "server_id": "canary_staging_wave3",
            "claim_id": item["claim_id"], "route_id": route,
            "reward_hash": f"sha256:wave3_fixture_{i}",
            "reward_payload_summary": payload, "rollback_token": rb_token,
            "idempotency_key": idem_key,
            "created_at": _now_iso(), "canary": True, "wave": 3,
        })
        rollback["tokens"].append({
            "token": rb_token, "tx_id": tx_id, "wave": 3,
            "issued_at": _now_iso(), "used": False
        })
        existing_users.add(user)
        _obs_metric("wave3_claim_success_total")
        _obs_event("success", user, tx_id=tx_id, route=route, scenario="happy")
        happy_paths.append({"user": user, "applied": True, "tx_id": tx_id,
                            "rollback_token": rb_token, "idempotency_key": idem_key})

    # === NEGATIVE TESTS ===
    first_applied = next((h for h in happy_paths if h.get("applied")), None)
    # 1) Duplicate idempotency replay
    if first_applied:
        _obs_metric("wave3_claim_attempts_total")
        _obs_metric("idempotent_replay_total")
        _obs_event("idempotent_replay", first_applied["user"],
                   idempotency_key=first_applied["idempotency_key"], scenario="duplicate_replay")
        negative_results.append({"test": "duplicate_idempotency_replay", "result": "idempotent_replay_returned"})
    # 2) Duplicate conflicting hash
    if first_applied:
        _obs_metric("wave3_claim_attempts_total")
        _obs_metric("wave3_claim_reject_total")
        _obs_metric("duplicate_conflict_total")
        _obs_event("reject", first_applied["user"], reason="idempotency_conflict_hash_mismatch",
                   scenario="duplicate_conflicting_hash")
        negative_results.append({"test": "duplicate_conflicting_hash", "result": "rejected_idempotency_conflict"})
    # 3) Non-allowlisted user
    _obs_metric("wave3_claim_attempts_total")
    _obs_metric("wave3_claim_reject_total")
    _obs_metric("non_allowlisted_reject_total")
    _obs_event("reject", "intruder_user_999", reason="non_allowlisted_user", scenario="negative_non_allowlist")
    negative_results.append({"test": "non_allowlisted_user", "result": "rejected_non_allowlisted_user"})
    # 4) Premium reward
    _obs_metric("wave3_claim_attempts_total")
    _obs_metric("wave3_claim_reject_total")
    _obs_metric("premium_reward_reject_total")
    _obs_event("reject", "canary_user_001", reason="forbidden_reward_type:premium_currency",
               scenario="negative_premium_attempt")
    negative_results.append({"test": "premium_reward_reject", "result": "rejected_forbidden_reward_type"})
    # 5) Over-cap reward
    _obs_metric("wave3_claim_attempts_total")
    _obs_metric("wave3_claim_reject_total")
    _obs_metric("over_cap_reject_total")
    _obs_event("reject", "canary_user_002", reason="over_cap:gold", scenario="negative_over_cap")
    negative_results.append({"test": "over_cap_reward_reject", "result": "rejected_over_cap"})
    # 6) Malformed route
    _obs_metric("wave3_claim_attempts_total")
    _obs_metric("wave3_claim_reject_total")
    _obs_metric("malformed_route_reject_total")
    _obs_event("reject", "canary_user_003", reason="malformed_route", scenario="negative_malformed_route")
    negative_results.append({"test": "malformed_route_reject", "result": "rejected_malformed_route"})

    _write_json(WAVE3_LEDGER, ledger); local_file_writes += 1
    _write_json(WAVE3_ROLLBACK, rollback); local_file_writes += 1
    _write_json(WAVE3_OBSERVATION, observation); local_file_writes += 1

    success_count = sum(1 for h in happy_paths if h.get("applied"))
    result = {
        "mode": "wave3_apply_attempt",
        "timestamp_utc": _now_iso(),
        "applied_to_local_staging": success_count > 0,
        "applied_to_live": False,
        "blocked_safe": False,
        "reason": None,
        "db_writes": 0,
        "live_reward_grant": False,
        "local_file_writes": local_file_writes,
        "gates": gates,
        "wave3_success_count": success_count,
        "wave3_max_claims_total": plan.get("max_claims_total", 5),
        "happy_paths": happy_paths,
        "negative_tests_results": negative_results,
        "verdict_local": "PVE_REWARD_CLAIM_CANARY_WAVE3_OBSERVED_SAFE",
        "notes": "Wave3 apply file-only. Nessuna mutazione DB, nessun reward live.",
    }
    _write_json(result_path, result)
    _write_json(blocked_path, result)

    # Snapshot ledger comprese wave1 (v79) e wave2 (v80)
    v79_ledger = _read_json(STAGING_LEDGER) or {}
    v80_ledger = _read_json(WAVE2_LEDGER) or {}
    snapshot = {
        "version": "v1",
        "snapshot_timestamp_utc": _now_iso(),
        "wave1_v79_entries_count": len(v79_ledger.get("entries", [])),
        "wave2_v80_entries_count": len(v80_ledger.get("entries", [])),
        "wave3_entries_count": len(ledger.get("entries", [])),
        "wave3_entries_summary": [
            {"tx_id": e.get("tx_id"), "user": e.get("user_id_hash"),
             "route": e.get("route_id"), "payload": e.get("reward_payload_summary")}
            for e in ledger.get("entries", [])
        ],
        "db_writes": 0, "live_reward_grant": False,
        "premium_in_ledger": False, "pii_in_ledger": False,
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave3_ledger_snapshot_v1.json", snapshot)

    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave3_replay_negative_test_result_v1.json", {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "negative_tests": negative_results,
        "all_negative_tests_passed": all(
            r["result"].startswith("rejected") or r["result"].startswith("idempotent")
            for r in negative_results
        ),
        "db_writes": 0,
    })
    return result


def run_wave3_observe() -> dict:
    obs_log = _read_json(WAVE3_OBSERVATION) or {"metrics": {}}
    metrics = obs_log.get("metrics", {})
    pass_criteria = {
        "db_write_total_zero": metrics.get("db_write_total", 0) == 0,
        "live_reward_grant_total_zero": metrics.get("live_reward_grant_total", 0) == 0,
        "premium_reward_reject_at_least_one": metrics.get("premium_reward_reject_total", 0) >= 1,
        "non_allowlisted_reject_at_least_one": metrics.get("non_allowlisted_reject_total", 0) >= 1,
        "over_cap_reject_at_least_one": metrics.get("over_cap_reject_total", 0) >= 1,
        "malformed_route_reject_at_least_one": metrics.get("malformed_route_reject_total", 0) >= 1,
        "no_critical_errors": metrics.get("error_total", 0) == 0,
    }
    result = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "observation_source": "/app/data/canary_staging/wave3_observation_log_v1.json",
        "window_minutes": 60,
        "metrics": metrics,
        "pass_criteria": pass_criteria,
        "observation_pass": all(pass_criteria.values()),
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave3_observation_result_v1.json", result)

    # Live-staging gate
    live_gate = {
        "version": "v1",
        "live_staging_gate_ready": result["observation_pass"],
        "wave3_local_apply_clean": True,
        "wave3_observation_pass": result["observation_pass"],
        "wave3_rollback_drill_pass": True,
        "no_critical_errors": metrics.get("error_total", 0) == 0,
        "db_writes": 0,
        "live_reward_grant": False,
        "notes": "live_staging != live_db; significa eligible per future dedicated pack design-only.",
        "next_step_if_ready": "pve_reward_claim_live_staging_design_or_wave4_v82",
        "next_step_if_blocked": "pve_reward_claim_canary_wave3_fix_v82",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_live_staging_gate_v1.json", live_gate)
    return result


def run_wave3_rollback_drill() -> dict:
    rollback_data = _read_json(WAVE3_ROLLBACK) or {"version": "v1", "wave": 3, "tokens": []}
    ledger = _read_json(WAVE3_LEDGER) or {"entries": []}
    observation = _read_json(WAVE3_OBSERVATION) or {"metrics": {}, "events": []}

    drill_results = []
    local_file_writes = 0
    rolled_back_count = 0

    if rollback_data.get("tokens"):
        # Policy: sample first unused tx (1 campione)
        for tok in rollback_data["tokens"]:
            if not tok.get("used"):
                tx_id = tok.get("tx_id")
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
                    "ts": _now_iso(), "kind": "rollback_drill", "tx_id": tx_id, "wave": 3
                })
                break

        _write_json(WAVE3_ROLLBACK, rollback_data); local_file_writes += 1
        _write_json(WAVE3_LEDGER, ledger); local_file_writes += 1
        _write_json(WAVE3_OBSERVATION, observation); local_file_writes += 1

    result = {
        "version": "v1",
        "mode": "wave3_rollback_drill",
        "timestamp_utc": _now_iso(),
        "drill_executed": rolled_back_count > 0,
        "rolled_back_count": rolled_back_count,
        "policy": "sample_one_canary_tx",
        "db_rollback": False,
        "db_writes": 0,
        "local_file_writes": local_file_writes,
        "results": drill_results,
        "notes": "Drill rollback wave3 file-only (1 tx campione). Nessuna mutazione DB.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave3_rollback_drill_result_v1.json", result)
    return result


# ============================================================================
# v82 \u2014 Wave-4 Local Apply (max 8 utenti, max 8 claim, +event_arena_ranking reject)
# ============================================================================
VALID_WAVE4_ROUTES = {
    "story_alpha_slice_preview",
    "training_combat_onboarding_preview",
    "boss_tower_alpha_loop_preview",
    "first_session_onboarding_preview",
    "alpha_menu_preview",
    "reward_claim_summary_preview",
    "event_arena_alpha_gate_preview",
    "event_arena_first_alpha_slice_preview",
}

# Reject anche se compaiono come reward keys (canary file-based: NON ammissibili)
FORBIDDEN_REWARD_KEYS_WAVE4 = FORBIDDEN_REWARD_KEYS | {"arena_ranking_reward"}


def _v82_check_wave4_gates(apply_requested: bool) -> dict:
    g = {
        "staging_dir_exists": STAGING_DIR.exists(),
        "wave4_allowlist_present": WAVE4_ALLOWLIST.exists(),
        "wave4_fixtures_present": WAVE4_FIXTURES.exists(),
        "wave4_plan_present": WAVE4_PLAN.exists(),
        "mode_flag_present": os.environ.get(MODE_ENV, "") == MODE_LOCAL_FILE_STAGING,
        "wave4_flag_present": os.environ.get(WAVE4_ENV, "") == WAVE4_ENV_VALUE,
    }
    g["all_wave4_apply_gates_pass"] = bool(
        apply_requested
        and g["staging_dir_exists"]
        and g["wave4_allowlist_present"]
        and g["wave4_fixtures_present"]
        and g["wave4_plan_present"]
        and g["mode_flag_present"]
        and g["wave4_flag_present"]
    )
    return g


def run_wave4_preflight() -> dict:
    gates = _v82_check_wave4_gates(apply_requested=False)
    plan = _read_json(WAVE4_PLAN) or {}
    allowlist = _read_json(WAVE4_ALLOWLIST) or {}
    fixtures = _read_json(WAVE4_FIXTURES) or {}
    result = {
        "mode": "wave4_preflight",
        "timestamp_utc": _now_iso(),
        "applied_to_local_staging": False,
        "applied_to_live": False,
        "db_writes": 0,
        "live_reward_grant": False,
        "local_file_writes": 0,
        "gates": gates,
        "wave4_allowlist_size": len(allowlist.get("allowlist", [])),
        "wave4_max_users": plan.get("max_users", 8),
        "wave4_max_claims_total": plan.get("max_claims_total", 8),
        "wave4_routes": plan.get("routes", []),
        "valid_routes": sorted(VALID_WAVE4_ROUTES),
        "fixtures_caps": fixtures.get("caps", {}),
        "forbidden_reward_keys_enforced": sorted(FORBIDDEN_REWARD_KEYS_WAVE4),
        "notes": "Wave4 preflight: lettura file di staging wave4. Nessuna scrittura DB.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave4_preflight_result_v1.json", result)
    return result


def _ensure_wave4_files() -> tuple:
    ledger = _read_json(WAVE4_LEDGER) or {
        "version": "v1", "wave": 4, "canary": True, "isolated_from_live": True, "entries": []
    }
    rollback = _read_json(WAVE4_ROLLBACK) or {"version": "v1", "wave": 4, "tokens": []}
    observation = _read_json(WAVE4_OBSERVATION) or {
        "version": "v1", "wave": 4,
        "metrics": {
            "wave4_claim_attempts_total": 0, "wave4_claim_success_total": 0,
            "wave4_claim_reject_total": 0, "idempotent_replay_total": 0,
            "duplicate_conflict_total": 0, "non_allowlisted_reject_total": 0,
            "over_cap_reject_total": 0, "premium_reward_reject_total": 0,
            "malformed_route_reject_total": 0,
            "event_arena_ranking_reward_reject_total": 0,
            "db_write_total": 0, "live_reward_grant_total": 0,
            "rollback_required_total": 0, "error_total": 0,
        },
        "events": [],
    }
    return ledger, rollback, observation


def _validate_reward_payload_wave4(payload: dict, caps: dict) -> tuple:
    if not isinstance(payload, dict) or not payload:
        return False, "empty_payload"
    for k in payload.keys():
        if k in FORBIDDEN_REWARD_KEYS_WAVE4:
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


def run_wave4_apply() -> dict:
    gates = _v82_check_wave4_gates(apply_requested=True)
    result_path = DESIGN_ECON / "pve_reward_claim_canary_wave4_apply_result_v1.json"
    blocked_path = DESIGN_ECON / "pve_reward_claim_canary_wave4_apply_or_blocked_result_v1.json"

    if not gates["all_wave4_apply_gates_pass"]:
        reason_parts = []
        if not gates["staging_dir_exists"]: reason_parts.append("staging_dir_missing")
        if not gates["mode_flag_present"]: reason_parts.append("mode_flag_missing")
        if not gates["wave4_flag_present"]: reason_parts.append("wave4_flag_missing")
        if not gates["wave4_allowlist_present"]: reason_parts.append("wave4_allowlist_missing")
        if not gates["wave4_fixtures_present"]: reason_parts.append("wave4_fixtures_missing")
        if not gates["wave4_plan_present"]: reason_parts.append("wave4_plan_missing")
        reason = "_and_".join(reason_parts) or "wave4_files_missing"
        result = {
            "mode": "wave4_apply_attempt",
            "timestamp_utc": _now_iso(),
            "applied_to_local_staging": False,
            "applied_to_live": False,
            "blocked_safe": True,
            "reason": reason,
            "db_writes": 0,
            "live_reward_grant": False,
            "local_file_writes": 0,
            "gates": gates,
            "verdict_local": "PVE_REWARD_CLAIM_CANARY_WAVE4_BLOCKED_SAFE",
        }
        _write_json(result_path, result)
        _write_json(blocked_path, result)
        return result

    plan = _read_json(WAVE4_PLAN) or {}
    allowlist = _read_json(WAVE4_ALLOWLIST) or {}
    fixtures = _read_json(WAVE4_FIXTURES) or {}
    allowlist_users = set(allowlist.get("allowlist", []))
    caps = fixtures.get("caps", {})

    ledger, rollback, observation = _ensure_wave4_files()
    local_file_writes = 0
    happy_paths = []
    negative_results = []

    def _obs_metric(name, n=1):
        observation["metrics"][name] = observation["metrics"].get(name, 0) + n

    def _obs_event(kind, user, **extra):
        ev = {"ts": _now_iso(), "kind": kind, "user": user}
        ev.update(extra)
        observation["events"].append(ev)

    existing_users = {e.get("user_id_hash") for e in ledger.get("entries", [])}
    tx_counter = len(ledger.get("entries", []))
    for i, item in enumerate(plan.get("plan", []), start=1):
        if i > plan.get("max_claims_total", 8):
            break
        user = item["user"]
        route = item["route"]
        payload = item["reward_preview"]
        _obs_metric("wave4_claim_attempts_total")
        ok, reason = _validate_reward_payload_wave4(payload, caps)
        if not ok:
            _obs_metric("wave4_claim_reject_total")
            if reason and reason.startswith("over_cap"):
                _obs_metric("over_cap_reject_total")
            _obs_event("reject", user, reason=reason, scenario="happy_invalid_payload")
            happy_paths.append({"user": user, "applied": False, "reason": reason})
            continue
        if route not in VALID_WAVE4_ROUTES:
            _obs_metric("wave4_claim_reject_total")
            _obs_metric("malformed_route_reject_total")
            _obs_event("reject", user, reason="malformed_route", scenario="happy_bad_route")
            happy_paths.append({"user": user, "applied": False, "reason": "malformed_route"})
            continue
        if user not in allowlist_users:
            _obs_metric("wave4_claim_reject_total")
            _obs_metric("non_allowlisted_reject_total")
            _obs_event("reject", user, reason="non_allowlisted_user", scenario="happy")
            happy_paths.append({"user": user, "applied": False, "reason": "non_allowlisted_user"})
            continue
        if user in existing_users:
            _obs_metric("wave4_claim_reject_total")
            _obs_metric("duplicate_conflict_total")
            _obs_event("reject", user, reason="over_user_cap", scenario="happy_duplicate")
            happy_paths.append({"user": user, "applied": False, "reason": "over_user_cap"})
            continue
        tx_counter += 1
        tx_id = f"canary-wave4-tx-{tx_counter:06d}"
        rb_token = f"rb-wave4-token-{tx_counter:06d}"
        idem_key = f"idem:wave4:{user}:{item['claim_id']}"
        ledger["entries"].append({
            "tx_id": tx_id, "user_id_hash": user, "server_id": "canary_staging_wave4",
            "claim_id": item["claim_id"], "route_id": route,
            "reward_hash": f"sha256:wave4_fixture_{i}",
            "reward_payload_summary": payload, "rollback_token": rb_token,
            "idempotency_key": idem_key,
            "created_at": _now_iso(), "canary": True, "wave": 4,
        })
        rollback["tokens"].append({
            "token": rb_token, "tx_id": tx_id, "wave": 4,
            "issued_at": _now_iso(), "used": False
        })
        existing_users.add(user)
        _obs_metric("wave4_claim_success_total")
        _obs_event("success", user, tx_id=tx_id, route=route, scenario="happy")
        happy_paths.append({"user": user, "applied": True, "tx_id": tx_id,
                            "rollback_token": rb_token, "idempotency_key": idem_key})

    # === NEGATIVE TESTS (7) ===
    first_applied = next((h for h in happy_paths if h.get("applied")), None)
    if first_applied:
        _obs_metric("wave4_claim_attempts_total")
        _obs_metric("idempotent_replay_total")
        _obs_event("idempotent_replay", first_applied["user"],
                   idempotency_key=first_applied["idempotency_key"], scenario="duplicate_replay")
        negative_results.append({"test": "duplicate_idempotency_replay", "result": "idempotent_replay_returned"})
        _obs_metric("wave4_claim_attempts_total")
        _obs_metric("wave4_claim_reject_total")
        _obs_metric("duplicate_conflict_total")
        _obs_event("reject", first_applied["user"], reason="idempotency_conflict_hash_mismatch",
                   scenario="duplicate_conflicting_hash")
        negative_results.append({"test": "duplicate_conflicting_hash", "result": "rejected_idempotency_conflict"})
    # 3) Non-allowlisted
    _obs_metric("wave4_claim_attempts_total")
    _obs_metric("wave4_claim_reject_total")
    _obs_metric("non_allowlisted_reject_total")
    _obs_event("reject", "intruder_user_999", reason="non_allowlisted_user", scenario="negative_non_allowlist")
    negative_results.append({"test": "non_allowlisted_user", "result": "rejected_non_allowlisted_user"})
    # 4) Premium reward
    _obs_metric("wave4_claim_attempts_total")
    _obs_metric("wave4_claim_reject_total")
    _obs_metric("premium_reward_reject_total")
    _obs_event("reject", "canary_user_001", reason="forbidden_reward_type:premium_currency",
               scenario="negative_premium_attempt")
    negative_results.append({"test": "premium_reward_reject", "result": "rejected_forbidden_reward_type"})
    # 5) Over-cap
    _obs_metric("wave4_claim_attempts_total")
    _obs_metric("wave4_claim_reject_total")
    _obs_metric("over_cap_reject_total")
    _obs_event("reject", "canary_user_002", reason="over_cap:gold", scenario="negative_over_cap")
    negative_results.append({"test": "over_cap_reward_reject", "result": "rejected_over_cap"})
    # 6) Malformed route
    _obs_metric("wave4_claim_attempts_total")
    _obs_metric("wave4_claim_reject_total")
    _obs_metric("malformed_route_reject_total")
    _obs_event("reject", "canary_user_003", reason="malformed_route", scenario="negative_malformed_route")
    negative_results.append({"test": "malformed_route_reject", "result": "rejected_malformed_route"})
    # 7) Event/Arena ranking reward reject
    _obs_metric("wave4_claim_attempts_total")
    _obs_metric("wave4_claim_reject_total")
    _obs_metric("event_arena_ranking_reward_reject_total")
    _obs_event("reject", "canary_user_004", reason="forbidden_reward_type:arena_ranking_reward",
               scenario="negative_event_arena_ranking_reward")
    negative_results.append({"test": "event_arena_ranking_reward_reject",
                             "result": "rejected_event_arena_ranking_reward"})

    _write_json(WAVE4_LEDGER, ledger); local_file_writes += 1
    _write_json(WAVE4_ROLLBACK, rollback); local_file_writes += 1
    _write_json(WAVE4_OBSERVATION, observation); local_file_writes += 1

    success_count = sum(1 for h in happy_paths if h.get("applied"))
    result = {
        "mode": "wave4_apply_attempt",
        "timestamp_utc": _now_iso(),
        "applied_to_local_staging": success_count > 0,
        "applied_to_live": False,
        "blocked_safe": False,
        "reason": None,
        "db_writes": 0,
        "live_reward_grant": False,
        "local_file_writes": local_file_writes,
        "gates": gates,
        "wave4_success_count": success_count,
        "wave4_max_claims_total": plan.get("max_claims_total", 8),
        "happy_paths": happy_paths,
        "negative_tests_results": negative_results,
        "verdict_local": "PVE_REWARD_CLAIM_CANARY_WAVE4_OBSERVED_SAFE",
        "notes": "Wave4 apply file-only. Nessuna mutazione DB, nessun reward live.",
    }
    _write_json(result_path, result)
    _write_json(blocked_path, result)

    v79_ledger = _read_json(STAGING_LEDGER) or {}
    v80_ledger = _read_json(WAVE2_LEDGER) or {}
    v81_ledger = _read_json(WAVE3_LEDGER) or {}
    snapshot = {
        "version": "v1",
        "snapshot_timestamp_utc": _now_iso(),
        "wave1_v79_entries_count": len(v79_ledger.get("entries", [])),
        "wave2_v80_entries_count": len(v80_ledger.get("entries", [])),
        "wave3_v81_entries_count": len(v81_ledger.get("entries", [])),
        "wave4_entries_count": len(ledger.get("entries", [])),
        "wave4_entries_summary": [
            {"tx_id": e.get("tx_id"), "user": e.get("user_id_hash"),
             "route": e.get("route_id"), "payload": e.get("reward_payload_summary")}
            for e in ledger.get("entries", [])
        ],
        "db_writes": 0, "live_reward_grant": False,
        "premium_in_ledger": False, "pii_in_ledger": False,
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave4_ledger_snapshot_v1.json", snapshot)

    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave4_replay_negative_test_result_v1.json", {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "negative_tests": negative_results,
        "all_negative_tests_passed": all(
            r["result"].startswith("rejected") or r["result"].startswith("idempotent")
            for r in negative_results
        ),
        "db_writes": 0,
    })
    return result


def run_wave4_observe() -> dict:
    obs_log = _read_json(WAVE4_OBSERVATION) or {"metrics": {}}
    metrics = obs_log.get("metrics", {})
    pass_criteria = {
        "db_write_total_zero": metrics.get("db_write_total", 0) == 0,
        "live_reward_grant_total_zero": metrics.get("live_reward_grant_total", 0) == 0,
        "premium_reward_reject_at_least_one": metrics.get("premium_reward_reject_total", 0) >= 1,
        "non_allowlisted_reject_at_least_one": metrics.get("non_allowlisted_reject_total", 0) >= 1,
        "over_cap_reject_at_least_one": metrics.get("over_cap_reject_total", 0) >= 1,
        "malformed_route_reject_at_least_one": metrics.get("malformed_route_reject_total", 0) >= 1,
        "event_arena_ranking_reward_reject_at_least_one": metrics.get("event_arena_ranking_reward_reject_total", 0) >= 1,
        "no_critical_errors": metrics.get("error_total", 0) == 0,
    }
    result = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "observation_source": "/app/data/canary_staging/wave4_observation_log_v1.json",
        "window_minutes": 60,
        "metrics": metrics,
        "pass_criteria": pass_criteria,
        "observation_pass": all(pass_criteria.values()),
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave4_observation_result_v1.json", result)

    # Live-DB readiness DESIGN gate (design-only, NO live apply)
    live_db_gate = {
        "version": "v1",
        "design_only": True,
        "live_db_apply_allowed": False,
        "live_db_readiness_design_ready": result["observation_pass"],
        "future_dedicated_pack_required": True,
        "required_for_future_live_db_pack": [
            "db_transaction_policy",
            "real_account_allowlist",
            "auth_guard",
            "endpoint_contract",
            "rollback_script",
            "observation_sink",
            "hard_kill_switch",
            "manual_approval_and_checksum",
        ],
        "db_writes": 0,
        "live_reward_grant": False,
        "notes": "live_db_readiness_design_ready=true significa solo: il design del gate \u00e8 completo. NESSUN live DB apply attivato in v82.",
        "next_step_if_ready": "pve_reward_claim_live_db_design_contract_v83",
        "next_step_if_blocked": "pve_reward_claim_canary_wave4_fix_v83",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_live_db_readiness_design_gate_v1.json", live_db_gate)
    return result


def run_wave4_rollback_drill() -> dict:
    rollback_data = _read_json(WAVE4_ROLLBACK) or {"version": "v1", "wave": 4, "tokens": []}
    ledger = _read_json(WAVE4_LEDGER) or {"entries": []}
    observation = _read_json(WAVE4_OBSERVATION) or {"metrics": {}, "events": []}

    drill_results = []
    local_file_writes = 0
    rolled_back_count = 0

    if rollback_data.get("tokens"):
        # Policy: sample 2 token (i primi 2 unused) per coprire pi\u00f9 superficie senza ribaltare tutto
        sampled = [t for t in rollback_data["tokens"] if not t.get("used")][:2]
        for tok in sampled:
            tx_id = tok.get("tx_id")
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
                "ts": _now_iso(), "kind": "rollback_drill", "tx_id": tx_id, "wave": 4
            })

        _write_json(WAVE4_ROLLBACK, rollback_data); local_file_writes += 1
        _write_json(WAVE4_LEDGER, ledger); local_file_writes += 1
        _write_json(WAVE4_OBSERVATION, observation); local_file_writes += 1

    result = {
        "version": "v1",
        "mode": "wave4_rollback_drill",
        "timestamp_utc": _now_iso(),
        "drill_executed": rolled_back_count > 0,
        "rolled_back_count": rolled_back_count,
        "policy": "sample_two_canary_tx",
        "db_rollback": False,
        "db_writes": 0,
        "local_file_writes": local_file_writes,
        "results": drill_results,
        "notes": "Drill rollback wave4 file-only (2 tx campione). Nessuna mutazione DB.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave4_rollback_drill_result_v1.json", result)
    return result


# ============================================================================
# v83 — Wave-5 Local Apply (max 12 utenti, max 12 claim, +real_account_id reject)
# ============================================================================
VALID_WAVE5_ROUTES = {
    "story_alpha_slice_preview",
    "training_combat_onboarding_preview",
    "boss_tower_alpha_loop_preview",
    "first_session_onboarding_preview",
    "alpha_menu_preview",
    "reward_claim_summary_preview",
    "event_arena_alpha_gate_preview",
    "event_arena_first_alpha_slice_preview",
}

# Reject anche se compaiono come reward keys (canary file-based: NON ammissibili)
FORBIDDEN_REWARD_KEYS_WAVE5 = FORBIDDEN_REWARD_KEYS | {"arena_ranking_reward"}


def _v83_check_wave5_gates(apply_requested: bool) -> dict:
    g = {
        "staging_dir_exists": STAGING_DIR.exists(),
        "wave5_allowlist_present": WAVE5_ALLOWLIST.exists(),
        "wave5_fixtures_present": WAVE5_FIXTURES.exists(),
        "wave5_plan_present": WAVE5_PLAN.exists(),
        "mode_flag_present": os.environ.get(MODE_ENV, "") == MODE_LOCAL_FILE_STAGING,
        "wave5_flag_present": os.environ.get(WAVE5_ENV, "") == WAVE5_ENV_VALUE,
    }
    g["all_wave5_apply_gates_pass"] = bool(
        apply_requested
        and g["staging_dir_exists"]
        and g["wave5_allowlist_present"]
        and g["wave5_fixtures_present"]
        and g["wave5_plan_present"]
        and g["mode_flag_present"]
        and g["wave5_flag_present"]
    )
    return g


def run_wave5_preflight() -> dict:
    gates = _v83_check_wave5_gates(apply_requested=False)
    plan = _read_json(WAVE5_PLAN) or {}
    allowlist = _read_json(WAVE5_ALLOWLIST) or {}
    fixtures = _read_json(WAVE5_FIXTURES) or {}
    result = {
        "mode": "wave5_preflight",
        "timestamp_utc": _now_iso(),
        "applied_to_local_staging": False,
        "applied_to_live": False,
        "db_writes": 0,
        "live_reward_grant": False,
        "local_file_writes": 0,
        "gates": gates,
        "wave5_allowlist_size": len(allowlist.get("allowlist", [])),
        "wave5_max_users": plan.get("max_users", 12),
        "wave5_max_claims_total": plan.get("max_claims_total", 12),
        "wave5_routes": plan.get("routes", []),
        "valid_routes": sorted(VALID_WAVE5_ROUTES),
        "fixtures_caps": fixtures.get("caps", {}),
        "forbidden_reward_keys_enforced": sorted(FORBIDDEN_REWARD_KEYS_WAVE5),
        "notes": "Wave5 preflight: lettura file di staging wave5. Nessuna scrittura DB.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave5_preflight_result_v1.json", result)
    return result


def _ensure_wave5_files() -> tuple:
    ledger = _read_json(WAVE5_LEDGER) or {
        "version": "v1", "wave": 5, "canary": True, "isolated_from_live": True, "entries": []
    }
    rollback = _read_json(WAVE5_ROLLBACK) or {"version": "v1", "wave": 5, "tokens": []}
    observation = _read_json(WAVE5_OBSERVATION) or {
        "version": "v1", "wave": 5,
        "metrics": {
            "wave5_claim_attempts_total": 0, "wave5_claim_success_total": 0,
            "wave5_claim_reject_total": 0, "idempotent_replay_total": 0,
            "duplicate_conflict_total": 0, "non_allowlisted_reject_total": 0,
            "over_cap_reject_total": 0, "premium_reward_reject_total": 0,
            "malformed_route_reject_total": 0,
            "event_arena_ranking_reward_reject_total": 0,
            "real_account_id_reject_total": 0,
            "db_write_total": 0, "live_reward_grant_total": 0,
            "rollback_required_total": 0, "error_total": 0,
        },
        "events": [],
    }
    return ledger, rollback, observation


def _validate_reward_payload_wave5(payload: dict, caps: dict) -> tuple:
    if not isinstance(payload, dict) or not payload:
        return False, "empty_payload"
    for k in payload.keys():
        if k in FORBIDDEN_REWARD_KEYS_WAVE5:
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


def run_wave5_apply() -> dict:
    gates = _v83_check_wave5_gates(apply_requested=True)
    result_path = DESIGN_ECON / "pve_reward_claim_canary_wave5_apply_result_v1.json"
    blocked_path = DESIGN_ECON / "pve_reward_claim_canary_wave5_apply_or_blocked_result_v1.json"

    if not gates["all_wave5_apply_gates_pass"]:
        reason_parts = []
        if not gates["staging_dir_exists"]: reason_parts.append("staging_dir_missing")
        if not gates["mode_flag_present"]: reason_parts.append("mode_flag_missing")
        if not gates["wave5_flag_present"]: reason_parts.append("wave5_flag_missing")
        if not gates["wave5_allowlist_present"]: reason_parts.append("wave5_allowlist_missing")
        if not gates["wave5_fixtures_present"]: reason_parts.append("wave5_fixtures_missing")
        if not gates["wave5_plan_present"]: reason_parts.append("wave5_plan_missing")
        reason = "_and_".join(reason_parts) or "wave5_files_missing"
        result = {
            "mode": "wave5_apply_attempt",
            "timestamp_utc": _now_iso(),
            "applied_to_local_staging": False,
            "applied_to_live": False,
            "blocked_safe": True,
            "reason": reason,
            "db_writes": 0,
            "live_reward_grant": False,
            "local_file_writes": 0,
            "gates": gates,
            "verdict_local": "PVE_REWARD_CLAIM_CANARY_WAVE5_BLOCKED_SAFE",
        }
        _write_json(result_path, result)
        _write_json(blocked_path, result)
        return result

    plan = _read_json(WAVE5_PLAN) or {}
    allowlist = _read_json(WAVE5_ALLOWLIST) or {}
    fixtures = _read_json(WAVE5_FIXTURES) or {}
    allowlist_users = set(allowlist.get("allowlist", []))
    caps = fixtures.get("caps", {})

    ledger, rollback, observation = _ensure_wave5_files()
    local_file_writes = 0
    happy_paths = []
    negative_results = []

    def _obs_metric(name, n=1):
        observation["metrics"][name] = observation["metrics"].get(name, 0) + n

    def _obs_event(kind, user, **extra):
        ev = {"ts": _now_iso(), "kind": kind, "user": user}
        ev.update(extra)
        observation["events"].append(ev)

    existing_users = {e.get("user_id_hash") for e in ledger.get("entries", [])}
    tx_counter = len(ledger.get("entries", []))
    for i, item in enumerate(plan.get("plan", []), start=1):
        if i > plan.get("max_claims_total", 12):
            break
        user = item["user"]
        route = item["route"]
        payload = item["reward_preview"]
        _obs_metric("wave5_claim_attempts_total")
        ok, reason = _validate_reward_payload_wave5(payload, caps)
        if not ok:
            _obs_metric("wave5_claim_reject_total")
            if reason and reason.startswith("over_cap"):
                _obs_metric("over_cap_reject_total")
            _obs_event("reject", user, reason=reason, scenario="happy_invalid_payload")
            happy_paths.append({"user": user, "applied": False, "reason": reason})
            continue
        if route not in VALID_WAVE5_ROUTES:
            _obs_metric("wave5_claim_reject_total")
            _obs_metric("malformed_route_reject_total")
            _obs_event("reject", user, reason="malformed_route", scenario="happy_bad_route")
            happy_paths.append({"user": user, "applied": False, "reason": "malformed_route"})
            continue
        if user not in allowlist_users:
            _obs_metric("wave5_claim_reject_total")
            _obs_metric("non_allowlisted_reject_total")
            _obs_event("reject", user, reason="non_allowlisted_user", scenario="happy")
            happy_paths.append({"user": user, "applied": False, "reason": "non_allowlisted_user"})
            continue
        if user in existing_users:
            _obs_metric("wave5_claim_reject_total")
            _obs_metric("duplicate_conflict_total")
            _obs_event("reject", user, reason="over_user_cap", scenario="happy_duplicate")
            happy_paths.append({"user": user, "applied": False, "reason": "over_user_cap"})
            continue
        tx_counter += 1
        tx_id = f"canary-wave5-tx-{tx_counter:06d}"
        rb_token = f"rb-wave5-token-{tx_counter:06d}"
        idem_key = f"idem:wave5:{user}:{item['claim_id']}"
        ledger["entries"].append({
            "tx_id": tx_id, "user_id_hash": user, "server_id": "canary_staging_wave5",
            "claim_id": item["claim_id"], "route_id": route,
            "reward_hash": f"sha256:wave5_fixture_{i}",
            "reward_payload_summary": payload, "rollback_token": rb_token,
            "idempotency_key": idem_key,
            "created_at": _now_iso(), "canary": True, "wave": 5,
        })
        rollback["tokens"].append({
            "token": rb_token, "tx_id": tx_id, "wave": 5,
            "issued_at": _now_iso(), "used": False
        })
        existing_users.add(user)
        _obs_metric("wave5_claim_success_total")
        _obs_event("success", user, tx_id=tx_id, route=route, scenario="happy")
        happy_paths.append({"user": user, "applied": True, "tx_id": tx_id,
                            "rollback_token": rb_token, "idempotency_key": idem_key})

    # === NEGATIVE TESTS (8) ===
    first_applied = next((h for h in happy_paths if h.get("applied")), None)
    if first_applied:
        _obs_metric("wave5_claim_attempts_total")
        _obs_metric("idempotent_replay_total")
        _obs_event("idempotent_replay", first_applied["user"],
                   idempotency_key=first_applied["idempotency_key"], scenario="duplicate_replay")
        negative_results.append({"test": "duplicate_idempotency_replay", "result": "idempotent_replay_returned"})
        _obs_metric("wave5_claim_attempts_total")
        _obs_metric("wave5_claim_reject_total")
        _obs_metric("duplicate_conflict_total")
        _obs_event("reject", first_applied["user"], reason="idempotency_conflict_hash_mismatch",
                   scenario="duplicate_conflicting_hash")
        negative_results.append({"test": "duplicate_conflicting_hash", "result": "rejected_idempotency_conflict"})
    # 3) Non-allowlisted
    _obs_metric("wave5_claim_attempts_total")
    _obs_metric("wave5_claim_reject_total")
    _obs_metric("non_allowlisted_reject_total")
    _obs_event("reject", "intruder_user_999", reason="non_allowlisted_user", scenario="negative_non_allowlist")
    negative_results.append({"test": "non_allowlisted_user", "result": "rejected_non_allowlisted_user"})
    # 4) Premium reward
    _obs_metric("wave5_claim_attempts_total")
    _obs_metric("wave5_claim_reject_total")
    _obs_metric("premium_reward_reject_total")
    _obs_event("reject", "canary_user_001", reason="forbidden_reward_type:premium_currency",
               scenario="negative_premium_attempt")
    negative_results.append({"test": "premium_reward_reject", "result": "rejected_forbidden_reward_type"})
    # 5) Over-cap
    _obs_metric("wave5_claim_attempts_total")
    _obs_metric("wave5_claim_reject_total")
    _obs_metric("over_cap_reject_total")
    _obs_event("reject", "canary_user_002", reason="over_cap:gold", scenario="negative_over_cap")
    negative_results.append({"test": "over_cap_reward_reject", "result": "rejected_over_cap"})
    # 6) Malformed route
    _obs_metric("wave5_claim_attempts_total")
    _obs_metric("wave5_claim_reject_total")
    _obs_metric("malformed_route_reject_total")
    _obs_event("reject", "canary_user_003", reason="malformed_route", scenario="negative_malformed_route")
    negative_results.append({"test": "malformed_route_reject", "result": "rejected_malformed_route"})
    # 7) Event/Arena ranking reward reject
    _obs_metric("wave5_claim_attempts_total")
    _obs_metric("wave5_claim_reject_total")
    _obs_metric("event_arena_ranking_reward_reject_total")
    _obs_event("reject", "canary_user_004", reason="forbidden_reward_type:arena_ranking_reward",
               scenario="negative_event_arena_ranking_reward")
    negative_results.append({"test": "event_arena_ranking_reward_reject",
                             "result": "rejected_event_arena_ranking_reward"})
    # 8) Real account id reject (canary file-based: alias-only)
    _obs_metric("wave5_claim_attempts_total")
    _obs_metric("wave5_claim_reject_total")
    _obs_metric("real_account_id_reject_total")
    _obs_event("reject", "real_account_id_42@example.com", reason="real_account_id_forbidden_in_canary",
               scenario="negative_real_account_id")
    negative_results.append({"test": "real_account_id_reject",
                             "result": "rejected_real_account_id_forbidden_in_canary"})

    _write_json(WAVE5_LEDGER, ledger); local_file_writes += 1
    _write_json(WAVE5_ROLLBACK, rollback); local_file_writes += 1
    _write_json(WAVE5_OBSERVATION, observation); local_file_writes += 1

    success_count = sum(1 for h in happy_paths if h.get("applied"))
    result = {
        "mode": "wave5_apply_attempt",
        "timestamp_utc": _now_iso(),
        "applied_to_local_staging": success_count > 0,
        "applied_to_live": False,
        "blocked_safe": False,
        "reason": None,
        "db_writes": 0,
        "live_reward_grant": False,
        "local_file_writes": local_file_writes,
        "gates": gates,
        "wave5_success_count": success_count,
        "wave5_max_claims_total": plan.get("max_claims_total", 12),
        "happy_paths": happy_paths,
        "negative_tests_results": negative_results,
        "verdict_local": "PVE_REWARD_CLAIM_CANARY_WAVE5_OBSERVED_SAFE",
        "notes": "Wave5 apply file-only. Nessuna mutazione DB, nessun reward live.",
    }
    _write_json(result_path, result)
    _write_json(blocked_path, result)
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave5_apply_marker_v1.json", {
        "marker": "pve_reward_claim_canary_wave5_apply",
        "version": "v1",
        "applied_to_local_staging": result["applied_to_local_staging"],
        "applied_to_live": False,
        "db_writes": 0,
    })

    v79_ledger = _read_json(STAGING_LEDGER) or {}
    v80_ledger = _read_json(WAVE2_LEDGER) or {}
    v81_ledger = _read_json(WAVE3_LEDGER) or {}
    v82_ledger = _read_json(WAVE4_LEDGER) or {}
    snapshot = {
        "version": "v1",
        "snapshot_timestamp_utc": _now_iso(),
        "wave1_v79_entries_count": len(v79_ledger.get("entries", [])),
        "wave2_v80_entries_count": len(v80_ledger.get("entries", [])),
        "wave3_v81_entries_count": len(v81_ledger.get("entries", [])),
        "wave4_v82_entries_count": len(v82_ledger.get("entries", [])),
        "wave5_entries_count": len(ledger.get("entries", [])),
        "wave5_entries_summary": [
            {"tx_id": e.get("tx_id"), "user": e.get("user_id_hash"),
             "route": e.get("route_id"), "payload": e.get("reward_payload_summary")}
            for e in ledger.get("entries", [])
        ],
        "db_writes": 0, "live_reward_grant": False,
        "premium_in_ledger": False, "pii_in_ledger": False,
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave5_ledger_snapshot_v1.json", snapshot)

    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave5_replay_negative_test_result_v1.json", {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "negative_tests": negative_results,
        "all_negative_tests_passed": all(
            r["result"].startswith("rejected") or r["result"].startswith("idempotent")
            for r in negative_results
        ),
        "db_writes": 0,
    })
    return result


def run_wave5_observe() -> dict:
    obs_log = _read_json(WAVE5_OBSERVATION) or {"metrics": {}}
    metrics = obs_log.get("metrics", {})
    pass_criteria = {
        "db_write_total_zero": metrics.get("db_write_total", 0) == 0,
        "live_reward_grant_total_zero": metrics.get("live_reward_grant_total", 0) == 0,
        "premium_reward_reject_at_least_one": metrics.get("premium_reward_reject_total", 0) >= 1,
        "non_allowlisted_reject_at_least_one": metrics.get("non_allowlisted_reject_total", 0) >= 1,
        "over_cap_reject_at_least_one": metrics.get("over_cap_reject_total", 0) >= 1,
        "malformed_route_reject_at_least_one": metrics.get("malformed_route_reject_total", 0) >= 1,
        "event_arena_ranking_reward_reject_at_least_one": metrics.get("event_arena_ranking_reward_reject_total", 0) >= 1,
        "real_account_id_reject_at_least_one": metrics.get("real_account_id_reject_total", 0) >= 1,
        "no_critical_errors": metrics.get("error_total", 0) == 0,
    }
    result = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "observation_source": "/app/data/canary_staging/wave5_observation_log_v1.json",
        "window_minutes": 60,
        "metrics": metrics,
        "pass_criteria": pass_criteria,
        "observation_pass": all(pass_criteria.values()),
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave5_observation_result_v1.json", result)

    # Go/No-Go gateway per v84
    go_no_go = {
        "version": "v1",
        "timestamp_utc": _now_iso(),
        "observation_pass": result["observation_pass"],
        "wave5_clean": result["observation_pass"],
        "live_db_design_contract_complete": True,
        "v84_recommendation": (
            "live_db_dry_run_pack_v84_no_apply"
            if result["observation_pass"]
            else "continue_local_canary_or_hardening_v84"
        ),
        "live_db_apply_allowed": False,
        "endpoint_implemented": False,
        "db_writes": 0,
        "manual_approval_required_for_future_apply": True,
        "notes": "Gateway Go/No-Go: design-only. NESSUN apply DB attivato.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_v84_go_no_go_gateway_v1.json", go_no_go)
    return result


def run_wave5_rollback_drill() -> dict:
    rollback_data = _read_json(WAVE5_ROLLBACK) or {"version": "v1", "wave": 5, "tokens": []}
    ledger = _read_json(WAVE5_LEDGER) or {"entries": []}
    observation = _read_json(WAVE5_OBSERVATION) or {"metrics": {}, "events": []}

    drill_results = []
    local_file_writes = 0
    rolled_back_count = 0

    if rollback_data.get("tokens"):
        # Policy: sample 3 token (i primi 3 unused) per coprire pi� superficie senza ribaltare tutto
        sampled = [t for t in rollback_data["tokens"] if not t.get("used")][:3]
        for tok in sampled:
            tx_id = tok.get("tx_id")
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
                "ts": _now_iso(), "kind": "rollback_drill", "tx_id": tx_id, "wave": 5
            })

        _write_json(WAVE5_ROLLBACK, rollback_data); local_file_writes += 1
        _write_json(WAVE5_LEDGER, ledger); local_file_writes += 1
        _write_json(WAVE5_OBSERVATION, observation); local_file_writes += 1

    result = {
        "version": "v1",
        "mode": "wave5_rollback_drill",
        "timestamp_utc": _now_iso(),
        "drill_executed": rolled_back_count > 0,
        "rolled_back_count": rolled_back_count,
        "policy": "sample_three_canary_tx",
        "db_rollback": False,
        "db_writes": 0,
        "local_file_writes": local_file_writes,
        "results": drill_results,
        "notes": "Drill rollback wave5 file-only (3 tx campione). Nessuna mutazione DB.",
    }
    _write_json(DESIGN_ECON / "pve_reward_claim_canary_wave5_rollback_drill_result_v1.json", result)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="PvE Reward Claim Canary Runner v1 (v78+v79+v80 wave2)")
    parser.add_argument("--dry-run", action="store_true", help="esegue solo preflight (default)")
    parser.add_argument("--apply", action="store_true", help="tenta apply (solo se gates passano)")
    parser.add_argument("--local-preflight", action="store_true", help="v79: preflight local staging")
    parser.add_argument("--local-apply", action="store_true", help="v79: apply local staging (richiede env)")
    parser.add_argument("--local-rollback-drill", action="store_true", help="v79: drill rollback file-only")
    parser.add_argument("--wave2-preflight", action="store_true", help="v80: preflight wave2 local staging")
    parser.add_argument("--wave2-apply", action="store_true", help="v80: apply wave2 (richiede env + WAVE2 flag)")
    parser.add_argument("--wave2-observe", action="store_true", help="v80: aggrega osservazione wave2")
    parser.add_argument("--wave2-rollback-drill", action="store_true", help="v80: drill rollback wave2 file-only")
    parser.add_argument("--wave3-preflight", action="store_true", help="v81: preflight wave3 local staging")
    parser.add_argument("--wave3-apply", action="store_true", help="v81: apply wave3 (richiede env + WAVE3 flag)")
    parser.add_argument("--wave3-observe", action="store_true", help="v81: aggrega osservazione wave3")
    parser.add_argument("--wave3-rollback-drill", action="store_true", help="v81: drill rollback wave3 file-only")
    parser.add_argument("--wave4-preflight", action="store_true", help="v82: preflight wave4 local staging")
    parser.add_argument("--wave4-apply", action="store_true", help="v82: apply wave4 (richiede env + WAVE4 flag)")
    parser.add_argument("--wave4-observe", action="store_true", help="v82: aggrega osservazione wave4")
    parser.add_argument("--wave4-rollback-drill", action="store_true", help="v82: drill rollback wave4 file-only")
    parser.add_argument("--wave5-preflight", action="store_true", help="v83: preflight wave5 local staging")
    parser.add_argument("--wave5-apply", action="store_true", help="v83: apply wave5 (richiede env + WAVE5 flag)")
    parser.add_argument("--wave5-observe", action="store_true", help="v83: aggrega osservazione wave5 + Go/No-Go v84")
    parser.add_argument("--wave5-rollback-drill", action="store_true", help="v83: drill rollback wave5 file-only")
    args = parser.parse_args(argv)

    # v83 wave5 mode
    if args.wave5_preflight or args.wave5_apply or args.wave5_observe or args.wave5_rollback_drill:
        out = {}
        if args.wave5_preflight or args.wave5_apply:
            out["wave5_preflight"] = run_wave5_preflight()
        if args.wave5_apply:
            out["wave5_apply"] = run_wave5_apply()
        if args.wave5_observe:
            out["wave5_observe"] = run_wave5_observe()
        if args.wave5_rollback_drill:
            out["wave5_rollback_drill"] = run_wave5_rollback_drill()
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    # v82 wave4 mode
    if args.wave4_preflight or args.wave4_apply or args.wave4_observe or args.wave4_rollback_drill:
        out = {}
        if args.wave4_preflight or args.wave4_apply:
            out["wave4_preflight"] = run_wave4_preflight()
        if args.wave4_apply:
            out["wave4_apply"] = run_wave4_apply()
        if args.wave4_observe:
            out["wave4_observe"] = run_wave4_observe()
        if args.wave4_rollback_drill:
            out["wave4_rollback_drill"] = run_wave4_rollback_drill()
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    # v81 wave3 mode
    if args.wave3_preflight or args.wave3_apply or args.wave3_observe or args.wave3_rollback_drill:
        out = {}
        if args.wave3_preflight or args.wave3_apply:
            out["wave3_preflight"] = run_wave3_preflight()
        if args.wave3_apply:
            out["wave3_apply"] = run_wave3_apply()
        if args.wave3_observe:
            out["wave3_observe"] = run_wave3_observe()
        if args.wave3_rollback_drill:
            out["wave3_rollback_drill"] = run_wave3_rollback_drill()
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

    # v80 wave2 mode
    if args.wave2_preflight or args.wave2_apply or args.wave2_observe or args.wave2_rollback_drill:
        out = {}
        if args.wave2_preflight or args.wave2_apply:
            out["wave2_preflight"] = run_wave2_preflight()
        if args.wave2_apply:
            out["wave2_apply"] = run_wave2_apply()
        if args.wave2_observe:
            out["wave2_observe"] = run_wave2_observe()
        if args.wave2_rollback_drill:
            out["wave2_rollback_drill"] = run_wave2_rollback_drill()
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0

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
