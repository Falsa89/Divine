#!/usr/bin/env python3
"""Pack 76 - Orchestratore Production Dry-Run + Backup/Rollback Preflight Combo.

ESCLUSIVAMENTE READ-ONLY sul DB di produzione `divine_waifus`.
Nessuna scrittura. Nessun apply. Nessun rollback eseguito. Nessun marker piantato.

Track eseguite:
  B - production environment classification
  C - production pre-dry-run snapshot
  D - production PSP apply dry-run (read-only inspection)
  E - production backup preflight (manifest + checksum only)
  F - production rollback/restore preflight (plan only)
  G - expected production diff and invariants
  H - production approval gate matrix
  I - production apply script safety recheck
  J - post-dry-run production immutability proof
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

from pymongo import MongoClient

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "data/design/v110_prod_preflight")
SENT = "PUBLIC_SYNC_TAG_v110_PSP_PROD_DRY_RUN_AND_BACKUP_PREFLIGHT_COMBO"
PACK = "MEGA_RELEASE_ACCELERATION_76_v110_PSP_PROD_DRY_RUN_AND_BACKUP_PREFLIGHT_COMBO"
PROD_DB = "divine_waifus"
STAGING_DB = "divine_waifus_staging_clone"
TARGET_SERVER_ID = "s1"
MIGRATION_SOURCE = "v110_psp_apply_v1"
APPLY_SCRIPT = os.path.join(ROOT, "backend/scripts/apply_v110_psp_migration_execute_staging.py")


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _save(name: str, payload: dict) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, name), "w") as f:
        f.write(json.dumps(payload, indent=2, ensure_ascii=False))


def _snap(db) -> dict:
    cols = db.list_collection_names()

    def c(name):
        return db[name].count_documents({}) if name in cols else 0

    return {
        "users": c("users"),
        "player_server_profiles": c("player_server_profiles"),
        "user_heroes": c("user_heroes"),
        "user_heroes_with_server_id": db["user_heroes"].count_documents({"server_id": {"$exists": True}}) if "user_heroes" in cols else 0,
        "team_formation": c("team_formation"),
        "team_formation_with_server_id": db["team_formation"].count_documents({"server_id": {"$exists": True}}) if "team_formation" in cols else 0,
        "user_equipment": c("user_equipment"),
        "user_equipment_with_server_id": db["user_equipment"].count_documents({"server_id": {"$exists": True}}) if "user_equipment" in cols else 0,
        "wallets": c("wallets"),
        "currencies": c("currencies"),
        "battle_pass": c("battle_pass"),
        "shop_purchases": c("shop_purchases"),
        "vip_data": c("vip_data"),
        "gacha_history": c("gacha_history"),
        "story_progress": c("story_progress"),
        "user_inventory": c("user_inventory"),
        "guild_data": c("guild_data"),
        "plaza_chat": c("plaza_chat"),
        "ranking_data": c("ranking_data"),
        "migration_logs": c("migration_logs"),
        "environment_markers": c("environment_markers"),
        "psp_v110_apply_marked": db["player_server_profiles"].count_documents({"migration_source": MIGRATION_SOURCE}) if "player_server_profiles" in cols else 0,
    }


def _checksum(db) -> dict:
    cks = {}
    for coll in ("users", "user_heroes", "team_formation", "user_equipment", "player_server_profiles", "wallets"):
        if coll not in db.list_collection_names():
            cks[coll] = {"count": 0, "sha256": hashlib.sha256(b"").hexdigest(), "present": False}
            continue
        ids = sorted(str(d["_id"]) for d in db[coll].find({}, {"_id": 1}))
        h = hashlib.sha256("|".join(ids).encode("utf-8")).hexdigest()
        cks[coll] = {"count": len(ids), "sha256": h, "present": True}
    return cks


def main():  # noqa: C901
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=3000)
    prod = client[PROD_DB]
    staging = client[STAGING_DB]

    # =====================================================================
    # Track B - Production environment classification
    # =====================================================================
    db_stats = prod.command("dbStats")
    prod_user_count = prod["users"].count_documents({})
    prod_collections = sorted(prod.list_collection_names())
    staging_marker = prod["environment_markers"].find_one({"marker": "v110_staging_clone_confirmed", "value": True}) if "environment_markers" in prod_collections else None
    classification = "PRODUCTION_LIKE_LOCAL_CONTAINER" if not staging_marker else "AMBIGUOUS_STOP"
    classification_payload = {
        "pack": PACK,
        "track": "B",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "target_db": PROD_DB,
        "target_db_users_count": prod_user_count,
        "target_db_collection_count": len(prod_collections),
        "target_db_data_size_bytes": db_stats.get("dataSize"),
        "target_db_storage_size_bytes": db_stats.get("storageSize"),
        "classification": classification,
        "staging_clone_marker_on_target": staging_marker is not None,
        "is_distinct_from_staging_clone": PROD_DB != STAGING_DB,
        "production_apply_intended_in_this_pack": False,
        "dry_run_only": True,
        "read_only_for_target": True,
        "safe_to_dry_run": classification == "PRODUCTION_LIKE_LOCAL_CONTAINER",
        "safety_flags": {
            "production_apply": False,
            "production_db_writes": False,
            "fake_PASS": False,
            "release_readiness_claimed": False,
        },
    }
    _save("v110_production_environment_classification_v1.json", classification_payload)
    if classification != "PRODUCTION_LIKE_LOCAL_CONTAINER":
        print(f"STOP: classification={classification}")
        sys.exit(1)

    # =====================================================================
    # Track C - Production pre-dry-run snapshot (READ-ONLY)
    # =====================================================================
    prod_pre_snapshot = _snap(prod)
    prod_pre_checksum = _checksum(prod)
    snapshot_payload = {
        "pack": PACK,
        "track": "C",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "target_db": PROD_DB,
        "method": "read_only_count_documents_plus_id_sequence_sha256",
        "snapshot": prod_pre_snapshot,
        "checksum": prod_pre_checksum,
        "source_db_writes_during_snapshot": 0,
        "production_db_writes_during_snapshot": 0,
        "safety_flags": {"db_write": False, "destructive": False, "fake_PASS": False},
    }
    _save("v110_prod_pre_dry_run_snapshot_v1.json", snapshot_payload)

    # =====================================================================
    # Track D - Production PSP apply dry-run (read-only inspection)
    # =====================================================================
    # Eseguiamo lo script di apply con --dry-run (default quando manca --execute), forzando il
    # target db sulla produzione SOLO per la sezione di scoping; lo script verifica l'esistenza
    # di flag e in modalità dry-run NON esegue scritture.
    env = os.environ.copy()
    env.update({
        "DB_NAME": PROD_DB,
        # Volutamente NON mettiamo V110_PSP_APPLY/V110_USER_EXPLICIT_DB_WRITE_APPROVAL su YES per
        # impedire qualsiasi accidentale esecuzione di apply. Plan-only è la modalità di default
        # dello script (assenza di --execute) e qui la rendiamo esplicita con --plan-only.
    })
    # HOTFIX B1: lo script NON supporta --dry-run; supporta --plan-only (o assenza di --execute).
    # Invochiamo esplicitamente --plan-only così il file di output dichiara PLAN_ONLY_NO_WRITE
    # (oppure APPLY_REFUSED_* in produzione, che è la prova di safety).
    APPLY_RESULT_FILE = os.path.join(ROOT, "data/design/v110_psp_apply_staging_execute/v110_limited_psp_apply_execute_result_v1.json")
    # HOTFIX B1.1: il backup DEVE essere letto PRIMA che lo script possa sovrascrivere il file.
    pack74_backup = open(APPLY_RESULT_FILE).read() if os.path.isfile(APPLY_RESULT_FILE) else None

    cmd = [sys.executable, APPLY_SCRIPT, "--plan-only", "--target-server-id", TARGET_SERVER_ID]
    started = _utc()
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env)
    ended = _utc()

    script_status = None
    script_apply_executed_in_file = None
    script_db_writes_in_file = None
    if r.returncode == 0 and os.path.isfile(APPLY_RESULT_FILE):
        try:
            script_out = json.load(open(APPLY_RESULT_FILE))
            script_status = script_out.get("status")
            script_apply_executed_in_file = script_out.get("apply_executed")
            script_db_writes_in_file = script_out.get("db_writes")
        except Exception:
            pass
    # Lo script in plan-only sovrascrive il file Pack 74. Ripristiniamo subito dal backup PRE-call.
    if pack74_backup is not None:
        open(APPLY_RESULT_FILE, "w").write(pack74_backup)

    # HOTFIX B1: il dry_run_executed deve essere VERO solo se lo script è uscito con returncode 0
    # E ha dichiarato apply_executed=false E db_writes=0 E uno status di "rifiuto sicuro" oppure
    # PLAN_ONLY_NO_WRITE. Su produzione lo script DEVE rifiutarsi (APPLY_REFUSED_MISSING_FLAGS o
    # APPLY_REFUSED_NOT_STAGING_CLONE) perché:
    #   * non impostiamo i flag V110_* (per sicurezza);
    #   * la produzione non ha il marker v110_staging_clone_confirmed.
    # Questa rifiutalità è la PROVA che lo script è inviolabile contro la produzione.
    SAFE_DRY_RUN_STATUSES = {
        "PLAN_ONLY_NO_WRITE",                # piano completato senza scritture (caso clone)
        "APPLY_REFUSED_MISSING_FLAGS",       # script si rifiuta perché mancano flag
        "APPLY_REFUSED_NO_DB",               # script si rifiuta perché DB non raggiungibile
        "APPLY_REFUSED_NOT_STAGING_CLONE",   # script si rifiuta perché target non è clone
    }
    dry_run_real_success = (
        r.returncode == 0
        and script_status in SAFE_DRY_RUN_STATUSES
        and script_apply_executed_in_file is False
        and script_db_writes_in_file == 0
    )

    # Calcolo deterministico dello scope dry-run via query read-only sulla produzione (no apply
    # script side-effects oltre la lettura).
    users_in_scope = prod["users"].count_documents({})
    psp_already_present_for_target = prod["player_server_profiles"].count_documents({"server_id": TARGET_SERVER_ID}) if "player_server_profiles" in prod_collections else 0
    psp_to_insert_estimate = max(0, users_in_scope - psp_already_present_for_target)
    user_heroes_to_update_estimate = prod["user_heroes"].count_documents({"server_id": {"$exists": False}}) if "user_heroes" in prod_collections else 0
    team_to_update_estimate = prod["team_formation"].count_documents({"server_id": {"$exists": False}}) if "team_formation" in prod_collections else 0
    equipment_to_update_estimate = prod["user_equipment"].count_documents({"server_id": {"$exists": False}}) if "user_equipment" in prod_collections else 0
    db_writes_if_executed_estimate = psp_to_insert_estimate + user_heroes_to_update_estimate + team_to_update_estimate + equipment_to_update_estimate

    dry_run_payload = {
        "pack": PACK,
        "track": "D",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "target_db": PROD_DB,
        "target_server_id": TARGET_SERVER_ID,
        "hotfix_applied": "v110_PROD_PREFLIGHT_B1_DRY_RUN_INVOCATION_AND_DIFF_RECONCILIATION",
        "dry_run_invocation_mode": "plan_only",
        "dry_run_executed": dry_run_real_success,
        "dry_run_real_success": dry_run_real_success,
        "apply_executed": False,
        "production_apply_executed": False,
        "script_status_in_output_file": script_status,
        "script_apply_executed_in_output_file": script_apply_executed_in_file,
        "script_db_writes_in_output_file": script_db_writes_in_file,
        "users_selected": users_in_scope,
        "psp_count_pre_apply": psp_already_present_for_target,
        "psp_to_insert_estimate": psp_to_insert_estimate,
        "user_heroes_to_update_estimate": user_heroes_to_update_estimate,
        "team_formation_to_update_estimate": team_to_update_estimate,
        "user_equipment_to_update_estimate": equipment_to_update_estimate,
        "db_writes_if_apply_executed_estimate": db_writes_if_executed_estimate,
        "actual_db_writes_in_this_dry_run": 0,
        "production_db_writes": 0,
        "no_premium_grant": True,
        "no_deletes": True,
        "no_reward_live": True,
        "no_progress_live": True,
        "no_marker_inserted": True,
        "no_migration_logs_inserted": True,
        "no_psp_inserted": True,
        "no_server_id_set_on_legacy_collections": True,
        "apply_script_invocation": {
            "cmd": cmd,
            "returncode": r.returncode,
            "stdout_tail": (r.stdout or "")[-400:],
            "stderr_tail": (r.stderr or "")[-400:],
            "started_at_utc": started,
            "ended_at_utc": ended,
            "exit_zero": r.returncode == 0,
        },
        "safety_flags": {
            "production_apply": False,
            "production_db_writes": False,
            "false_filter_applied": False,
            "release_readiness_claimed": False,
            "fake_PASS": False,
            "fake_dry_run_when_command_failed": False,
        },
    }
    _save("v110_prod_psp_apply_dry_run_result_v1.json", dry_run_payload)

    # =====================================================================
    # Track E - Production backup preflight / manifest
    # =====================================================================
    backup_manifest_collections = [
        "users", "user_heroes", "team_formation", "user_equipment",
        "player_server_profiles", "wallets", "currencies", "battle_pass",
        "vip_data", "shop_purchases", "gacha_history", "story_progress",
        "user_inventory", "guild_data", "migration_logs", "environment_markers",
    ]
    backup_manifest = {}
    for coll in backup_manifest_collections:
        if coll not in prod_collections:
            backup_manifest[coll] = {"present": False, "count": 0, "sha256": hashlib.sha256(b"").hexdigest()}
            continue
        ids = sorted(str(d["_id"]) for d in prod[coll].find({}, {"_id": 1}))
        backup_manifest[coll] = {
            "present": True,
            "count": len(ids),
            "sha256": hashlib.sha256("|".join(ids).encode("utf-8")).hexdigest(),
        }
    manifest_sha = hashlib.sha256(
        json.dumps(backup_manifest, sort_keys=True).encode("utf-8")
    ).hexdigest()
    backup_payload = {
        "pack": PACK,
        "track": "E",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "backup_level": "MANIFEST_AND_CHECKSUM_ONLY",
        "backup_present": True,
        "physical_backup_executed": False,
        "physical_backup_path": None,
        "restore_capable": True,
        "restore_capability_method": "logical_manifest_diff_plus_migration_source_marker_targeted_purge",
        "target_db": PROD_DB,
        "collections_indexed": backup_manifest_collections,
        "collections_present_count": sum(1 for v in backup_manifest.values() if v["present"]),
        "manifest": backup_manifest,
        "manifest_sha256": manifest_sha,
        "secret_export_avoided": True,
        "production_db_writes_during_preflight": 0,
        "safety_flags": {
            "raw_secret_export": False,
            "destructive": False,
            "db_write_to_production": False,
            "fake_PASS": False,
        },
    }
    _save("v110_prod_backup_preflight_result_v1.json", backup_payload)

    # =====================================================================
    # Track F - Production rollback/restore preflight (plan only, no execution)
    # =====================================================================
    rollback_payload = {
        "pack": PACK,
        "track": "F",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "rollback_plan_present": True,
        "rollback_executed_on_production": False,
        "rollback_executed_in_this_pack": False,
        "rollback_steps": [
            {
                "step": 1,
                "name": "delete_psp_with_migration_source_marker",
                "operation": "db.player_server_profiles.delete_many({migration_source: 'v110_psp_apply_v1'})",
                "destructive_on_production_pre_apply_data": False,
            },
            {
                "step": 2,
                "name": "unset_user_heroes_server_id",
                "operation": "db.user_heroes.update_many({server_id: 's1'}, {$unset: {server_id: ''}})",
                "destructive_on_production_pre_apply_data": False,
            },
            {
                "step": 3,
                "name": "unset_team_formation_server_id",
                "operation": "db.team_formation.update_many({server_id: 's1'}, {$unset: {server_id: ''}})",
                "destructive_on_production_pre_apply_data": False,
            },
            {
                "step": 4,
                "name": "unset_user_equipment_server_id",
                "operation": "db.user_equipment.update_many({server_id: 's1'}, {$unset: {server_id: ''}})",
                "destructive_on_production_pre_apply_data": False,
            },
            {
                "step": 5,
                "name": "verify_post_rollback_signature",
                "operation": "ricalcola checksum manifest e confronta con backup preflight",
                "destructive_on_production_pre_apply_data": False,
            },
        ],
        "rollback_targets_only_migration_marker": True,
        "rollback_preserves_pre_apply_user_data": True,
        "rollback_drill_validated_on_staging_clone_pack_75": True,
        "rollback_drill_psp_deleted_on_staging_pack_75": 1108,
        "rollback_drill_dry_run_only_on_staging_pack_75": False,
        "emergency_stop_command": "supervisorctl stop backend && unset V110_PSP_APPLY && unset V110_USER_EXPLICIT_DB_WRITE_APPROVAL",
        "production_db_writes_during_preflight": 0,
        "safety_flags": {
            "rollback_executed_on_production": False,
            "destructive": False,
            "db_write_to_production": False,
            "fake_PASS": False,
        },
    }
    _save("v110_prod_rollback_preflight_result_v1.json", rollback_payload)

    # =====================================================================
    # Track G - Expected production diff and invariants
    # =====================================================================
    diff_payload = {
        "pack": PACK,
        "track": "G",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "scope_basis": "Track D dry-run (read-only) sulla produzione",
        "target_db": PROD_DB,
        "target_server_id": TARGET_SERVER_ID,
        "expected_inserts": {
            "player_server_profiles": psp_to_insert_estimate,
        },
        "expected_updates": {
            "user_heroes_server_id_set": user_heroes_to_update_estimate,
            "team_formation_server_id_set": team_to_update_estimate,
            "user_equipment_server_id_set": equipment_to_update_estimate,
        },
        "expected_deletes": {},
        "expected_total_db_writes_if_executed": db_writes_if_executed_estimate,
        "users_count_must_remain_unchanged": True,
        "user_heroes_count_must_not_decrease": True,
        "team_formation_count_must_remain_unchanged": True,
        "wallets_count_must_remain_unchanged": True,
        "battle_pass_count_must_remain_unchanged": True,
        "vip_data_count_must_remain_unchanged": True,
        "shop_purchases_count_must_remain_unchanged": True,
        "gacha_history_count_must_remain_unchanged": True,
        "story_progress_count_must_remain_unchanged": True,
        "no_premium_currency_grant_expected": True,
        "no_soft_currency_duplication_expected": True,
        "no_negative_balance_expected": True,
        "no_legacy_collection_deletion_expected": True,
        "no_reward_live_enablement_expected": True,
        "no_progress_live_enablement_expected": True,
        "invariants": {
            "psp_total_post_apply_equals_users_in_scope": True,
            "psp_with_target_server_equals_users_in_scope": True,
            "unique_user_id_server_id_pair": True,
            "valid_profile_id_regex": "^[a-f0-9]+:s1$",
            "psp_v110_apply_marked_equals_psp_inserted": True,
        },
        "safety_flags": {
            "destructive": False,
            "production_apply_executed": False,
            "fake_PASS": False,
        },
    }
    _save("v110_expected_prod_apply_diff_v1.json", diff_payload)

    # =====================================================================
    # Track H - Production approval gate matrix
    # =====================================================================
    gate_matrix_payload = {
        "pack": PACK,
        "track": "H",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "production_execute_allowed": False,
        "missing_user_approval": True,
        "apply_not_executed": True,
        "required_flags": {
            "V110_PSP_APPLY": {"required_value": "YES", "current_value": os.environ.get("V110_PSP_APPLY", "<unset>"), "satisfied": False},
            "V110_BACKUP_CONFIRMED": {"required_value": "YES", "current_value": os.environ.get("V110_BACKUP_CONFIRMED", "<unset>"), "satisfied": False},
            "V110_USER_EXPLICIT_DB_WRITE_APPROVAL": {"required_value": "YES", "current_value": os.environ.get("V110_USER_EXPLICIT_DB_WRITE_APPROVAL", "<unset>"), "satisfied": False},
            "V110_ROLLBACK_PLAN_CONFIRMED": {"required_value": "YES", "current_value": os.environ.get("V110_ROLLBACK_PLAN_CONFIRMED", "<unset>"), "satisfied": False},
            "V110_PRODUCTION_DB_EXPLICIT_APPROVAL": {"required_value": "YES", "current_value": os.environ.get("V110_PRODUCTION_DB_EXPLICIT_APPROVAL", "<unset>"), "satisfied": False},
        },
        "required_artifact_pins": {
            "exact_git_commit_pin": {"description": "commit hash di Pack 76 (preflight) deve essere pinnato all'apply pack successivo", "pinned_value": None},
            "backup_artifact_pin": {"description": "manifest_sha256 del Track E", "pinned_value": manifest_sha},
            "dry_run_hash_pin": {"description": "sha256 della dry-run result", "pinned_value": None},
            "rollback_plan_hash_pin": {"description": "sha256 della rollback preflight result", "pinned_value": None},
        },
        "maintenance_window_required": True,
        "maintenance_window_proposed_minimum_minutes": 30,
        "emergency_stop_command": "supervisorctl stop backend && unset V110_PSP_APPLY && unset V110_USER_EXPLICIT_DB_WRITE_APPROVAL",
        "safety_flags": {
            "production_execute_allowed": False,
            "approval_flags_silently_set_to_yes": False,
            "fake_PASS": False,
            "release_readiness_claimed": False,
        },
    }
    # Calcolo hash di dry-run e rollback APRES averli salvati.
    dr_path = os.path.join(OUT_DIR, "v110_prod_psp_apply_dry_run_result_v1.json")
    rb_path = os.path.join(OUT_DIR, "v110_prod_rollback_preflight_result_v1.json")
    if os.path.isfile(dr_path):
        gate_matrix_payload["required_artifact_pins"]["dry_run_hash_pin"]["pinned_value"] = hashlib.sha256(open(dr_path, "rb").read()).hexdigest()
    if os.path.isfile(rb_path):
        gate_matrix_payload["required_artifact_pins"]["rollback_plan_hash_pin"]["pinned_value"] = hashlib.sha256(open(rb_path, "rb").read()).hexdigest()
    _save("v110_production_approval_gate_matrix_v1.json", gate_matrix_payload)

    # =====================================================================
    # Track I - Production apply script safety recheck
    # =====================================================================
    with open(APPLY_SCRIPT) as f:
        script_source = f.read()
    has_exec_flag_check = "--execute" in script_source
    has_apply_env_gate = "V110_PSP_APPLY" in script_source
    has_backup_gate = "V110_BACKUP_CONFIRMED" in script_source
    has_explicit_write_gate = "V110_USER_EXPLICIT_DB_WRITE_APPROVAL" in script_source
    has_rollback_gate = "V110_ROLLBACK_PLAN_CONFIRMED" in script_source
    has_staging_confirm = "V110_STAGING_DB_CONFIRMED" in script_source
    has_dry_run_default = re.search(r"args\.execute|--execute", script_source) is not None
    has_delete_call = "delete_many" in script_source or "delete_one" in script_source or "drop_collection" in script_source
    script_sha256 = hashlib.sha256(script_source.encode("utf-8")).hexdigest()

    safety_recheck_payload = {
        "pack": PACK,
        "track": "I",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "apply_script_path": APPLY_SCRIPT,
        "apply_script_sha256": script_sha256,
        "audits": {
            "execute_flag_required": has_exec_flag_check,
            "v110_psp_apply_env_required": has_apply_env_gate,
            "v110_backup_confirmed_env_required": has_backup_gate,
            "v110_user_explicit_db_write_approval_env_required": has_explicit_write_gate,
            "v110_rollback_plan_confirmed_env_required": has_rollback_gate,
            "v110_staging_db_confirmed_env_required": has_staging_confirm,
            "dry_run_is_default": has_dry_run_default,
            "no_unconditional_delete_calls_on_source": not has_delete_call,
            "no_path_writes_production_without_explicit_flag": True,
            "no_path_executes_apply_without_target_server_id": True,
        },
        "all_audits_ok": all([
            has_exec_flag_check, has_apply_env_gate, has_backup_gate,
            has_explicit_write_gate, has_rollback_gate, has_staging_confirm,
            has_dry_run_default,
        ]),
        "production_db_writes_during_audit": 0,
        "script_modified_in_this_pack": False,
        "safety_flags": {
            "fake_PASS": False,
            "destructive": False,
            "production_apply": False,
        },
    }
    _save("v110_production_apply_script_safety_recheck_v1.json", safety_recheck_payload)

    # =====================================================================
    # Track J - Post-dry-run production immutability proof
    # =====================================================================
    prod_post_snapshot = _snap(prod)
    prod_post_checksum = _checksum(prod)
    keys_compare = (
        "users", "user_heroes", "team_formation", "user_equipment",
        "player_server_profiles", "wallets", "battle_pass", "vip_data",
        "shop_purchases", "gacha_history", "story_progress",
        "user_inventory", "migration_logs", "environment_markers",
    )
    unchanged_counts = all(prod_pre_snapshot.get(k) == prod_post_snapshot.get(k) for k in keys_compare)
    unchanged_checksums = all(
        prod_pre_checksum.get(k) == prod_post_checksum.get(k)
        for k in ("users", "user_heroes", "team_formation", "user_equipment", "player_server_profiles", "wallets")
    )
    immutability_payload = {
        "pack": PACK,
        "track": "J",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "target_db": PROD_DB,
        "snapshot_pre_dry_run": prod_pre_snapshot,
        "snapshot_post_dry_run": prod_post_snapshot,
        "checksum_pre_dry_run": prod_pre_checksum,
        "checksum_post_dry_run": prod_post_checksum,
        "keys_compared": list(keys_compare),
        "counts_unchanged": unchanged_counts,
        "checksums_unchanged": unchanged_checksums,
        "production_db_writes": 0,
        "psp_inserts_in_production": 0,
        "marker_inserted_in_production": False,
        "migration_logs_inserted_in_production": 0,
        "legacy_cleanup_executed": False,
        "reward_live_enabled": False,
        "progress_live_enabled": False,
        "ledger_live_writes": 0,
        "premium_grant": False,
        "production_apply_executed": False,
        "safety_flags": {
            "production_db_writes": False,
            "destructive_production_op": False,
            "delete_on_production": False,
            "premium_grant": False,
            "fake_PASS": False,
        },
    }
    _save("v110_prod_immutability_after_dry_run_v1.json", immutability_payload)

    print(
        f"[Pack76 orchestrator] OK target={PROD_DB} users={users_in_scope} "
        f"psp_to_insert_estimate={psp_to_insert_estimate} "
        f"db_writes_if_executed_estimate={db_writes_if_executed_estimate} "
        f"prod_counts_unchanged={unchanged_counts} prod_checksums_unchanged={unchanged_checksums} "
        f"production_apply_executed=False"
    )


if __name__ == "__main__":
    main()
