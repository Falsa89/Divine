"""economy_ephemeral_simulation_invariant_report_dry_run.py

v50 — Track A
Ephemeral Simulation Invariant Report (DRY-RUN, in-memory only).

Imports ONLY the in-memory v49 ephemeral simulator. Aggregates a report
over 8 operation families x 9 scenarios = 72 scenarios and verifies the
hard invariants:
- real_db_writes == 0 (always)
- production_db_touched == false (always)
- mongo_url_used / pymongo_used / motor_used / env_read == false
- filesystem_writes == 0
- total_simulated_ephemeral_writes_count > 0

Strict properties:
- NO route exposure. NO server.py changes. NO endpoint introduction.
- NO real DB connection. NO env read. NO filesystem writes at runtime.
- NO live apply. NO mutation on production.

Public API:
- build_invariant_report() -> dict
- build_config_block()      -> dict
- _test_reset()             -> None
"""
from __future__ import annotations

from typing import Any, Dict, List

from utils.economy_ephemeral_test_db_live_simulation_dry_run import (
    run_full_pre_flight,
    _test_reset as _v49_reset,
    SUPPORTED_FAMILIES as _V49_FAMILIES,
    SCENARIOS as _V49_SCENARIOS,
)

CONTRACT_VERSION = "economy_ephemeral_simulation_invariant_report_dry_run_v1"
DRY_RUN_ONLY = True
DB_WRITES = 0
REAL_DB_WRITES = 0
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
NO_ROUTE_EXPOSURE = True
NO_SERVER_PY_CHANGE = True


def build_invariant_report() -> Dict[str, Any]:
    """Run v49 full pre-flight and build the aggregated invariant report."""
    _v49_reset()
    pf = run_full_pre_flight()
    families = pf.get("families") or {}
    expected_families = list(_V49_FAMILIES)
    expected_scenarios = list(_V49_SCENARIOS)
    total_scenarios_expected = len(expected_families) * len(expected_scenarios)

    invariants: List[Dict[str, Any]] = []
    total_simulated_writes = 0
    scenarios_evaluated = 0
    all_invariants_ok = True

    for fam in expected_families:
        fr = families.get(fam) or {}
        # Per-family aggregate invariants
        per_fam_real_db_writes = int(fr.get("real_db_writes") or 0)
        per_fam_prod_touched = bool(fr.get("production_db_touched"))
        per_fam_mongo = bool(fr.get("mongo_url_used"))
        per_fam_pymongo = bool(fr.get("pymongo_used"))
        per_fam_motor = bool(fr.get("motor_used"))
        per_fam_env = bool(fr.get("env_read"))
        per_fam_fs = int(fr.get("filesystem_writes") or 0)
        per_fam_live = bool(fr.get("live_apply_allowed"))
        per_fam_writes = int(fr.get("simulated_ephemeral_writes_count") or 0)
        per_fam_all_ok = bool(fr.get("all_ok"))
        per_fam_scenarios = fr.get("scenarios") or []

        fam_invariant_ok = (
            per_fam_real_db_writes == 0
            and per_fam_prod_touched is False
            and per_fam_mongo is False
            and per_fam_pymongo is False
            and per_fam_motor is False
            and per_fam_env is False
            and per_fam_fs == 0
            and per_fam_live is False
            and per_fam_all_ok is True
            and set(per_fam_scenarios) == set(expected_scenarios)
        )
        if not fam_invariant_ok:
            all_invariants_ok = False

        # Per-scenario invariants
        results = fr.get("results") or []
        scenarios_evaluated += len(results)
        for r in results:
            if int(r.get("real_db_writes") or 0) != 0:
                all_invariants_ok = False
                fam_invariant_ok = False
            if bool(r.get("production_db_touched")) is not False:
                all_invariants_ok = False
                fam_invariant_ok = False
            if bool(r.get("mongo_url_used")) is not False:
                all_invariants_ok = False
                fam_invariant_ok = False
            if bool(r.get("pymongo_used")) is not False:
                all_invariants_ok = False
                fam_invariant_ok = False
            if bool(r.get("motor_used")) is not False:
                all_invariants_ok = False
                fam_invariant_ok = False
            if bool(r.get("env_read")) is not False:
                all_invariants_ok = False
                fam_invariant_ok = False
            if int(r.get("filesystem_writes") or 0) != 0:
                all_invariants_ok = False
                fam_invariant_ok = False
            if bool(r.get("live_apply_allowed")) is not False:
                all_invariants_ok = False
                fam_invariant_ok = False
            if not bool(r.get("ok")):
                all_invariants_ok = False
                fam_invariant_ok = False

        total_simulated_writes += per_fam_writes
        invariants.append({
            "operation_family": fam,
            "scenarios_executed": len(results),
            "scenarios_expected": len(expected_scenarios),
            "all_ok": fam_invariant_ok,
            "real_db_writes": per_fam_real_db_writes,
            "production_db_touched": per_fam_prod_touched,
            "mongo_url_used": per_fam_mongo,
            "pymongo_used": per_fam_pymongo,
            "motor_used": per_fam_motor,
            "env_read": per_fam_env,
            "filesystem_writes": per_fam_fs,
            "live_apply_allowed": per_fam_live,
            "simulated_ephemeral_writes_count": per_fam_writes,
        })

    if total_simulated_writes <= 0:
        all_invariants_ok = False
    if scenarios_evaluated != total_scenarios_expected:
        all_invariants_ok = False

    return {
        "enabled": True,
        "contract_version": CONTRACT_VERSION,
        "dry_run_only": DRY_RUN_ONLY,
        "operation_families_count": len(expected_families),
        "scenarios_per_family": len(expected_scenarios),
        "total_scenarios_expected": total_scenarios_expected,
        "scenarios_evaluated": scenarios_evaluated,
        "total_simulated_ephemeral_writes_count": total_simulated_writes,
        "all_invariants_ok": all_invariants_ok,
        "real_db_writes": REAL_DB_WRITES,
        "db_writes": DB_WRITES,
        "production_db_touched": PRODUCTION_DB_TOUCHED,
        "mongo_url_used": MONGO_URL_USED,
        "pymongo_used": PYMONGO_USED,
        "motor_used": MOTOR_USED,
        "env_read": ENV_READ,
        "filesystem_writes": FILESYSTEM_WRITES,
        "persisted": PERSISTED,
        "live_apply_allowed": LIVE_APPLY_ALLOWED,
        "live_enforcement_enabled": LIVE_ENFORCEMENT_ENABLED,
        "preview_request_blocked": PREVIEW_REQUEST_BLOCKED,
        "no_route_exposure": NO_ROUTE_EXPOSURE,
        "no_server_py_change": NO_SERVER_PY_CHANGE,
        "pii_safe": True,
        "raw_payload_captured": False,
        "per_family": invariants,
    }


def build_config_block() -> Dict[str, Any]:
    return {
        "enabled": True,
        "contract_version": CONTRACT_VERSION,
        "dry_run_only": DRY_RUN_ONLY,
        "operation_families_count": len(_V49_FAMILIES),
        "scenarios_per_family": len(_V49_SCENARIOS),
        "db_writes": DB_WRITES,
        "real_db_writes": REAL_DB_WRITES,
        "production_db_touched": PRODUCTION_DB_TOUCHED,
        "mongo_url_used": MONGO_URL_USED,
        "pymongo_used": PYMONGO_USED,
        "motor_used": MOTOR_USED,
        "env_read": ENV_READ,
        "filesystem_writes": FILESYSTEM_WRITES,
        "live_apply_allowed": LIVE_APPLY_ALLOWED,
        "live_enforcement_enabled": LIVE_ENFORCEMENT_ENABLED,
        "preview_request_blocked": PREVIEW_REQUEST_BLOCKED,
        "no_route_exposure": NO_ROUTE_EXPOSURE,
        "no_server_py_change": NO_SERVER_PY_CHANGE,
    }


def _test_reset() -> None:
    """Validator/test hook: forward to v49 reset."""
    _v49_reset()
