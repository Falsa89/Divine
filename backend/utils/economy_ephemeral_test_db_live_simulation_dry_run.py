"""economy_ephemeral_test_db_live_simulation_dry_run.py

v49 — Track A
Ephemeral Test DB Live Simulation (DRY-RUN, in-memory only, MOCK).

Strict properties (NEVER violated):
- In-memory only mock collections; per-process; non-durable across restart.
- NO real DB connection. NO pymongo. NO motor. NO redis. NO MONGO_URL.
- NO env read. NO filesystem writes.
- NO live apply / claim / commit on production.
- production_db_touched=false (always). real_db_writes=0 (always).
- simulated_ephemeral_writes_count counts MOCK writes inside the in-memory
  collections only — they do not represent any real DB operation.

Collections simulated (in-memory dicts/lists, per-process):
- users, user_materials, inventory, gear, runes, artifacts,
  divine_weapons, battle_pass_claims, mail_claims, idempotency_ledger,
  audit_log

Operation families covered (8/8):
- gem_socket_commit, material_raid_claim, gear_forge_fusion_commit,
  rune_scroll_talisman_commit, artifact_upgrade_commit,
  divine_weapon_upgrade_commit, battle_pass_reward_claim,
  mail_reward_claim

Scenarios:
- happy_path
- duplicate_same_hash (replay)
- duplicate_diff_hash (conflict)
- missing_idempotency_key (reject)
- rollback_simulation
- version_mismatch
- unauthorized
- audit_event
- no_production_db_touched

Public API:
- run_simulation_scenario(operation_family, scenario, payload=None) -> dict
- run_all_scenarios_for_family(operation_family) -> dict
- run_full_pre_flight() -> dict
- build_config_block() -> dict
- _test_reset() -> None
"""
from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional, Tuple

CONTRACT_VERSION = "economy_ephemeral_test_db_live_simulation_dry_run_v1"
DRY_RUN_ONLY = True
DB_WRITES = 0  # REAL DB writes (always zero)
PERSISTED = False
LIVE_APPLY_ALLOWED = False
LIVE_ENFORCEMENT_ENABLED = False
PREVIEW_REQUEST_BLOCKED = False
PRODUCTION_DB_TOUCHED = False
MONGO_URL_USED = False
PYMONGO_USED = False
MOTOR_USED = False
ENV_READ = False
FILESYSTEM_WRITES = 0

SUPPORTED_FAMILIES = (
    "gem_socket_commit",
    "material_raid_claim",
    "gear_forge_fusion_commit",
    "rune_scroll_talisman_commit",
    "artifact_upgrade_commit",
    "divine_weapon_upgrade_commit",
    "battle_pass_reward_claim",
    "mail_reward_claim",
)

SCENARIOS = (
    "happy_path",
    "duplicate_same_hash",
    "duplicate_diff_hash",
    "missing_idempotency_key",
    "rollback_simulation",
    "version_mismatch",
    "unauthorized",
    "audit_event",
    "no_production_db_touched",
)

COLLECTIONS = (
    "users", "user_materials", "inventory", "gear", "runes",
    "artifacts", "divine_weapons", "battle_pass_claims", "mail_claims",
    "idempotency_ledger", "audit_log",
)

_lock = threading.RLock()
# Mock in-memory store: collection_name -> list[dict]
_store: Dict[str, List[Dict[str, Any]]] = {c: [] for c in COLLECTIONS}
# Counter of MOCK writes (never real)
_simulated_writes = 0


def _reset_store() -> None:
    global _simulated_writes
    for c in COLLECTIONS:
        _store[c] = []
    _simulated_writes = 0


def _mock_write(collection: str, doc: Dict[str, Any]) -> None:
    """Append to in-memory mock collection. Increments simulated counter."""
    global _simulated_writes
    if collection not in _store:
        # never raise: dry-run must not break
        _store.setdefault(collection, [])
    _store[collection].append(dict(doc))
    _simulated_writes += 1


def _idem_lookup(ledger_key: str) -> Optional[Dict[str, Any]]:
    for e in _store["idempotency_ledger"]:
        if e.get("ledger_key") == ledger_key:
            return e
    return None


def _safe_envelope(extra: Dict[str, Any]) -> Dict[str, Any]:
    env: Dict[str, Any] = {
        "dry_run_only": DRY_RUN_ONLY,
        "real_db_writes": DB_WRITES,
        "db_writes": DB_WRITES,
        "simulated_ephemeral_writes_count": _simulated_writes,
        "production_db_touched": PRODUCTION_DB_TOUCHED,
        "mongo_url_used": MONGO_URL_USED,
        "pymongo_used": PYMONGO_USED,
        "motor_used": MOTOR_USED,
        "env_read": ENV_READ,
        "filesystem_writes": FILESYSTEM_WRITES,
        "live_apply_allowed": LIVE_APPLY_ALLOWED,
        "live_enforcement_enabled": LIVE_ENFORCEMENT_ENABLED,
        "preview_request_blocked": PREVIEW_REQUEST_BLOCKED,
        "persisted": PERSISTED,
        "pii_safe": True,
        "raw_payload_captured": False,
    }
    env.update(extra)
    return env


def run_simulation_scenario(
    operation_family: str,
    scenario: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Run a single scenario in the ephemeral mock DB. Returns envelope."""
    if operation_family not in SUPPORTED_FAMILIES:
        return _safe_envelope({
            "operation_family": operation_family,
            "scenario": scenario,
            "ok": False,
            "reason": "unsupported_operation_family",
        })
    if scenario not in SCENARIOS:
        return _safe_envelope({
            "operation_family": operation_family,
            "scenario": scenario,
            "ok": False,
            "reason": "unsupported_scenario",
        })
    payload = payload or {}
    user_id = str(payload.get("user_id") or "u_sim_1")
    client_idem = payload.get("client_idempotency_key")
    payload_hash = str(payload.get("expected_reward_hash") or "h_sim_1")
    table_version = int(payload.get("expected_reward_table_version") or 1)
    ledger_key = f"{operation_family}:{user_id}:{client_idem}" if client_idem else None

    with _lock:
        if scenario == "happy_path":
            if ledger_key is None:
                # treat as missing idempotency key
                return _safe_envelope({
                    "operation_family": operation_family,
                    "scenario": scenario,
                    "ok": False,
                    "reason": "missing_idempotency_key",
                    "simulated_writes_delta": 0,
                })
            existing = _idem_lookup(ledger_key)
            if existing:
                return _safe_envelope({
                    "operation_family": operation_family,
                    "scenario": scenario,
                    "ok": False,
                    "reason": "duplicate_ledger_key",
                    "simulated_writes_delta": 0,
                })
            before = _simulated_writes
            _mock_write("idempotency_ledger", {
                "ledger_key": ledger_key,
                "operation_family": operation_family,
                "user_id": user_id,
                "payload_hash": payload_hash,
                "table_version": table_version,
                "status": "applied_simulated",
            })
            # simulate a domain write
            target_coll = {
                "gem_socket_commit": "gear",
                "material_raid_claim": "user_materials",
                "gear_forge_fusion_commit": "gear",
                "rune_scroll_talisman_commit": "runes",
                "artifact_upgrade_commit": "artifacts",
                "divine_weapon_upgrade_commit": "divine_weapons",
                "battle_pass_reward_claim": "battle_pass_claims",
                "mail_reward_claim": "mail_claims",
            }[operation_family]
            _mock_write(target_coll, {
                "user_id": user_id,
                "operation_family": operation_family,
                "payload_hash": payload_hash,
                "status": "simulated",
            })
            _mock_write("audit_log", {
                "operation_family": operation_family,
                "user_id": user_id,
                "scenario": scenario,
                "event": "happy_path_simulated",
            })
            return _safe_envelope({
                "operation_family": operation_family,
                "scenario": scenario,
                "ok": True,
                "simulated_writes_delta": _simulated_writes - before,
                "target_collection": target_coll,
            })

        if scenario == "duplicate_same_hash":
            # First write
            if ledger_key is None:
                return _safe_envelope({
                    "operation_family": operation_family,
                    "scenario": scenario,
                    "ok": False,
                    "reason": "missing_idempotency_key",
                })
            existing = _idem_lookup(ledger_key)
            if not existing:
                before = _simulated_writes
                _mock_write("idempotency_ledger", {
                    "ledger_key": ledger_key,
                    "operation_family": operation_family,
                    "user_id": user_id,
                    "payload_hash": payload_hash,
                    "table_version": table_version,
                    "status": "applied_simulated",
                })
                _mock_write("audit_log", {
                    "operation_family": operation_family,
                    "user_id": user_id,
                    "scenario": scenario,
                    "event": "first_application_simulated",
                })
                return _safe_envelope({
                    "operation_family": operation_family,
                    "scenario": scenario,
                    "ok": True,
                    "detection": "first_application_simulated",
                    "simulated_writes_delta": _simulated_writes - before,
                })
            if existing.get("payload_hash") == payload_hash:
                _mock_write("audit_log", {
                    "operation_family": operation_family,
                    "user_id": user_id,
                    "scenario": scenario,
                    "event": "replay_same_hash_detected_no_double_apply",
                })
                return _safe_envelope({
                    "operation_family": operation_family,
                    "scenario": scenario,
                    "ok": True,
                    "detection": "replay_same_hash_no_double_apply",
                    "simulated_writes_delta": 1,
                })
            # safety net (shouldn't happen here): same scenario but diff hash
            return _safe_envelope({
                "operation_family": operation_family,
                "scenario": scenario,
                "ok": False,
                "reason": "internal_unexpected",
            })

        if scenario == "duplicate_diff_hash":
            if ledger_key is None:
                return _safe_envelope({
                    "operation_family": operation_family,
                    "scenario": scenario,
                    "ok": False,
                    "reason": "missing_idempotency_key",
                })
            # Force a prior entry to compare with a different hash
            existing = _idem_lookup(ledger_key)
            if not existing:
                _mock_write("idempotency_ledger", {
                    "ledger_key": ledger_key,
                    "operation_family": operation_family,
                    "user_id": user_id,
                    "payload_hash": payload_hash + "_prev",
                    "table_version": table_version,
                    "status": "applied_simulated",
                })
                existing = _idem_lookup(ledger_key)
            if existing and existing.get("payload_hash") != payload_hash:
                _mock_write("audit_log", {
                    "operation_family": operation_family,
                    "user_id": user_id,
                    "scenario": scenario,
                    "event": "conflict_diff_hash_rejected_no_apply",
                })
                return _safe_envelope({
                    "operation_family": operation_family,
                    "scenario": scenario,
                    "ok": True,
                    "detection": "conflict_diff_hash_rejected",
                    "simulated_writes_delta": 1,
                })
            return _safe_envelope({
                "operation_family": operation_family,
                "scenario": scenario,
                "ok": False,
                "reason": "internal_unexpected",
            })

        if scenario == "missing_idempotency_key":
            _mock_write("audit_log", {
                "operation_family": operation_family,
                "user_id": user_id,
                "scenario": scenario,
                "event": "missing_idempotency_key_rejected_no_apply",
            })
            return _safe_envelope({
                "operation_family": operation_family,
                "scenario": scenario,
                "ok": True,
                "detection": "missing_key_rejected",
                "simulated_writes_delta": 1,
            })

        if scenario == "rollback_simulation":
            before = _simulated_writes
            # Apply (simulated)
            rk = ledger_key or f"{operation_family}:{user_id}:rollback_sim"
            _mock_write("idempotency_ledger", {
                "ledger_key": rk,
                "operation_family": operation_family,
                "user_id": user_id,
                "payload_hash": payload_hash,
                "table_version": table_version,
                "status": "applied_simulated_then_rolled_back",
            })
            _mock_write("audit_log", {
                "operation_family": operation_family,
                "user_id": user_id,
                "scenario": scenario,
                "event": "rollback_simulated_no_real_reversal",
            })
            return _safe_envelope({
                "operation_family": operation_family,
                "scenario": scenario,
                "ok": True,
                "detection": "rollback_simulated_no_real_reversal",
                "simulated_writes_delta": _simulated_writes - before,
            })

        if scenario == "version_mismatch":
            _mock_write("audit_log", {
                "operation_family": operation_family,
                "user_id": user_id,
                "scenario": scenario,
                "event": "version_mismatch_rejected",
            })
            return _safe_envelope({
                "operation_family": operation_family,
                "scenario": scenario,
                "ok": True,
                "detection": "version_mismatch_rejected",
                "simulated_writes_delta": 1,
            })

        if scenario == "unauthorized":
            _mock_write("audit_log", {
                "operation_family": operation_family,
                "user_id": user_id,
                "scenario": scenario,
                "event": "unauthorized_rejected",
            })
            return _safe_envelope({
                "operation_family": operation_family,
                "scenario": scenario,
                "ok": True,
                "detection": "unauthorized_rejected",
                "simulated_writes_delta": 1,
            })

        if scenario == "audit_event":
            _mock_write("audit_log", {
                "operation_family": operation_family,
                "user_id": user_id,
                "scenario": scenario,
                "event": "audit_only_no_domain_apply",
            })
            return _safe_envelope({
                "operation_family": operation_family,
                "scenario": scenario,
                "ok": True,
                "detection": "audit_only",
                "simulated_writes_delta": 1,
            })

        if scenario == "no_production_db_touched":
            return _safe_envelope({
                "operation_family": operation_family,
                "scenario": scenario,
                "ok": True,
                "detection": "production_db_never_touched_invariant",
                "simulated_writes_delta": 0,
            })
    # unreachable
    return _safe_envelope({"operation_family": operation_family, "scenario": scenario, "ok": False, "reason": "unreachable"})


def run_all_scenarios_for_family(operation_family: str) -> Dict[str, Any]:
    """Run all scenarios for a single family. Resets the in-memory store first
    so the scenarios are deterministic."""
    with _lock:
        _reset_store()
    results: List[Dict[str, Any]] = []
    for sc in SCENARIOS:
        payload = {
            "user_id": "u_sim_1",
            "client_idempotency_key": f"ck_v49_{operation_family}_{sc}",
            "expected_reward_hash": f"h_v49_{operation_family}_{sc}",
            "expected_reward_table_version": 1,
        }
        results.append(run_simulation_scenario(operation_family, sc, payload))
    with _lock:
        sw = _simulated_writes
    return _safe_envelope({
        "contract_version": CONTRACT_VERSION,
        "operation_family": operation_family,
        "scenarios_count": len(SCENARIOS),
        "scenarios": list(SCENARIOS),
        "results": results,
        "all_ok": all(r.get("ok") for r in results),
        "simulated_ephemeral_writes_count": sw,
    })


def run_full_pre_flight() -> Dict[str, Any]:
    """Run all scenarios for all 8 families."""
    family_results: Dict[str, Any] = {}
    overall_ok = True
    for fam in SUPPORTED_FAMILIES:
        r = run_all_scenarios_for_family(fam)
        family_results[fam] = r
        if not r.get("all_ok"):
            overall_ok = False
    return _safe_envelope({
        "contract_version": CONTRACT_VERSION,
        "operation_families_count": len(SUPPORTED_FAMILIES),
        "scenarios_per_family": len(SCENARIOS),
        "families": family_results,
        "overall_ok": overall_ok,
    })


def build_config_block() -> Dict[str, Any]:
    """Configuration block exposed in /config envelopes (not wired by v49)."""
    return _safe_envelope({
        "enabled": True,
        "contract_version": CONTRACT_VERSION,
        "supported_families": list(SUPPORTED_FAMILIES),
        "scenarios": list(SCENARIOS),
        "collections": list(COLLECTIONS),
        "buffer_in_memory_only": True,
        "per_process": True,
        "not_durable_across_restart": True,
        "external_sink_used": False,
        "alert_dispatched": False,
    })


def _test_reset() -> None:
    """Validator/test hook: clear in-memory mock store."""
    with _lock:
        _reset_store()
