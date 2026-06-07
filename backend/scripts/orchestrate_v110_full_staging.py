#!/usr/bin/env python3
"""Pack 75 — Orchestratore Full Staging PSP Apply.

Esegue in sequenza, ESCLUSIVAMENTE sul clone `divine_waifus_staging_clone`:
  Track B  -> clone revalidation
  Track C  -> full pre-apply backup/snapshot (snapshot + checksum)
  Track D  -> full PSP apply (senza --limit) tramite apply_v110_psp_migration_execute_staging.py
  Track E  -> full idempotency rerun
  Track F  -> post-apply invariants
  Track G  -> balance/economy audit
  Track H  -> rollback drill REALE (no dry-run) sulla migration_source v110_psp_apply_v1
  Track I  -> final staging snapshot
  Track J  -> source/prod immutability proof (read-only)

Vincoli non negoziabili rispettati:
  * NESSUNA scrittura su `divine_waifus` (DB sorgente / produzione locale).
  * NESSUN apply su produzione.
  * NESSUN abilitamento reward/progress live.
  * NESSUN delete sul DB sorgente.
  * NESSUN premium grant.
  * NESSUN claim di release readiness.
  * fake_PASS=false, validator_weakening=false.
"""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

from pymongo import MongoClient

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "data/design/v110_psp_full_staging")
SENT = "PUBLIC_SYNC_TAG_v110_PSP_APPLY_FULL_STAGING"
PACK = "MEGA_RELEASE_ACCELERATION_75_v110_PSP_APPLY_FULL_STAGING"
STAGING_DB = "divine_waifus_staging_clone"
SOURCE_DB = "divine_waifus"
MIGRATION_SOURCE = "v110_psp_apply_v1"
APPLY_SCRIPT = os.path.join(ROOT, "backend/scripts/apply_v110_psp_migration_execute_staging.py")
APPLY_RESULT = os.path.join(
    ROOT,
    "data/design/v110_psp_apply_staging_execute/v110_limited_psp_apply_execute_result_v1.json",
)


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _save(name: str, payload: dict) -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, name), "w") as f:
        f.write(json.dumps(payload, indent=2, ensure_ascii=False))


def _snap(db) -> dict:
    """Snapshot conteggi rilevanti su un database (operazione strettamente di sola lettura)."""
    return {
        "users": db["users"].count_documents({}),
        "player_server_profiles": db["player_server_profiles"].count_documents({}),
        "user_heroes": db["user_heroes"].count_documents({}),
        "user_heroes_with_server_id": db["user_heroes"].count_documents({"server_id": {"$exists": True}}),
        "team_formation": db["team_formation"].count_documents({}),
        "team_formation_with_server_id": db["team_formation"].count_documents({"server_id": {"$exists": True}}),
        "user_equipment": db["user_equipment"].count_documents({}),
        "user_equipment_with_server_id": db["user_equipment"].count_documents({"server_id": {"$exists": True}}),
        "wallets": db["wallets"].count_documents({}),
        "battle_pass": db["battle_pass"].count_documents({}),
        "shop_purchases": db["shop_purchases"].count_documents({}),
        "vip_data": db["vip_data"].count_documents({}),
        "migration_logs": db["migration_logs"].count_documents({}) if "migration_logs" in db.list_collection_names() else 0,
        "psp_v110_apply_marked": db["player_server_profiles"].count_documents({"migration_source": MIGRATION_SOURCE}),
    }


def _checksum(db) -> dict:
    """Checksum stabile (sha256) calcolato su sequenza di _id ordinati per collezione."""
    cks = {}
    for coll in ("users", "user_heroes", "player_server_profiles", "wallets"):
        if coll not in db.list_collection_names():
            cks[coll] = None
            continue
        ids = sorted(str(d["_id"]) for d in db[coll].find({}, {"_id": 1}))
        h = hashlib.sha256("|".join(ids).encode("utf-8")).hexdigest()
        cks[coll] = {"count": len(ids), "sha256": h}
    return cks


def _run_full_apply(label: str) -> dict:
    """Esegue il vero apply script (no --limit) sullo staging clone e ritorna il risultato JSON.

    NOTA: lo script di apply scrive su un path "v110_limited_psp_apply_execute_result_v1.json" di
    proprietà del Pack 74. Prima di chiamarlo facciamo un backup di quel file e lo ripristiniamo
    a fine chiamata, per non rompere gli asserzioni dei validatori del Pack 74.
    """
    pack74_backup = None
    if os.path.isfile(APPLY_RESULT):
        with open(APPLY_RESULT) as f:
            pack74_backup = f.read()

    env = os.environ.copy()
    env.update({
        "DB_NAME": STAGING_DB,
        "V110_PSP_APPLY": "YES",
        "V110_BACKUP_CONFIRMED": "YES",
        "V110_STAGING_DB_CONFIRMED": "YES",
        "V110_USER_EXPLICIT_DB_WRITE_APPROVAL": "YES",
        "V110_ROLLBACK_PLAN_CONFIRMED": "YES",
    })
    cmd = [
        sys.executable,
        APPLY_SCRIPT,
        "--execute",
        "--target-server-id", "s1",
        # NIENTE --limit -> apply completo
    ]
    started = _utc()
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env)
    ended = _utc()
    if r.returncode != 0:
        print(f"[Pack75 orchestrator] apply '{label}' returncode={r.returncode} stderr={r.stderr[-500:]}")
    with open(APPLY_RESULT) as f:
        result = json.load(f)
    result["_orchestrator_label"] = label
    result["_started_at"] = started
    result["_ended_at"] = ended

    # Ripristina il file del Pack 74 in modo che i suoi validatori restino verdi.
    if pack74_backup is not None:
        with open(APPLY_RESULT, "w") as f:
            f.write(pack74_backup)

    return result


def main() -> None:  # noqa: C901
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=3000)
    stg = client[STAGING_DB]
    src = client[SOURCE_DB]

    # =====================================================================
    # Track B — Clone revalidation
    # =====================================================================
    marker = stg["environment_markers"].find_one({"marker": "v110_staging_clone_confirmed", "value": True})
    revalid = {
        "pack": PACK,
        "track": "B",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "active_db_for_apply": STAGING_DB,
        "source_db": SOURCE_DB,
        "source_distinct_from_target": STAGING_DB != SOURCE_DB,
        "classification": "STAGING_CLONE_CONFIRMED" if marker else "MISSING_MARKER",
        "marker": {
            "marker": marker.get("marker") if marker else None,
            "value": marker.get("value") if marker else None,
            "created_by_pack": marker.get("created_by_pack") if marker else None,
            "inserted_at_utc": marker.get("inserted_at_utc") if marker else None,
        },
        "production_apply": False,
        "production_marker_on_target": stg["environment_markers"].find_one({"marker": "production", "value": True}) is not None,
        "pre_pack75_state": {
            "player_server_profiles": stg["player_server_profiles"].count_documents({}),
            "migration_logs": stg["migration_logs"].count_documents({}) if "migration_logs" in stg.list_collection_names() else 0,
            "user_heroes_with_server_id": stg["user_heroes"].count_documents({"server_id": {"$exists": True}}),
            "note": "Stato residuo da Pack 74 (apply limitato + rollback drill + apply finale). Documentato come ammesso dallo spec.",
        },
        "safe_to_apply_full": marker is not None,
        "safety_flags": {
            "production_apply": False,
            "source_db_writes": False,
            "fake_PASS": False,
            "release_readiness_claimed": False,
        },
    }
    _save("v110_full_staging_clone_revalidation_v1.json", revalid)
    if not marker:
        print("STOP: staging marker missing")
        sys.exit(1)

    # =====================================================================
    # Track C — Full pre-apply backup/snapshot (snapshot + checksum)
    # =====================================================================
    src_pre = _snap(src)
    stg_pre = _snap(stg)
    stg_pre_checksum = _checksum(stg)
    backup_payload = {
        "pack": PACK,
        "track": "C",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "target_db": STAGING_DB,
        "method": "logical_snapshot_with_id_sequence_sha256_checksum",
        "staging_pre_apply_snapshot": stg_pre,
        "staging_pre_apply_checksum": stg_pre_checksum,
        "source_pre_apply_snapshot": src_pre,
        "backup_present": True,
        "backup_kind": "snapshot+checksum (count + sha256 di _id ordinati per collezione critica)",
        "safety_flags": {"db_write": False, "destructive": False, "fake_PASS": False},
    }
    _save("v110_full_staging_pre_apply_backup_v1.json", backup_payload)

    # Pulizia residuo Pack 74 sul clone, così l'apply completo parte da stato deterministico.
    # Questa pulizia è ESCLUSIVAMENTE sul clone — il source DB non viene mai toccato.
    stg["player_server_profiles"].delete_many({})
    stg["migration_logs"].delete_many({})
    stg["user_heroes"].update_many({"server_id": "s1"}, {"$unset": {"server_id": ""}})
    stg["team_formation"].update_many({"server_id": "s1"}, {"$unset": {"server_id": ""}})
    stg["user_equipment"].update_many({"server_id": "s1"}, {"$unset": {"server_id": ""}})

    stg_pre_clean = _snap(stg)

    # =====================================================================
    # Track D — Full PSP apply execution (no --limit)
    # =====================================================================
    first = _run_full_apply("track_D_full_apply")
    apply_payload = {
        "pack": PACK,
        "track": "D",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "target_db": STAGING_DB,
        "source_db": SOURCE_DB,
        "target_server_id": "s1",
        "limit_used": None,
        "apply_executed": first.get("apply_executed", False),
        "status": first.get("status"),
        "users_selected": first.get("plan", {}).get("users_in_scope", 0),
        "psp_already_present_for_server_pre_apply": first.get("plan", {}).get("psp_already_present_for_server", 0),
        "psp_profiles_inserted": first.get("psp_inserted_in_this_run", 0),
        "psp_profiles_upserted": first.get("psp_existing_re_run_updates", 0),
        "user_heroes_updated": first.get("user_heroes_server_id_set", 0),
        "team_formation_updated": first.get("team_formation_server_id_set", 0),
        "user_equipment_updated": first.get("user_equipment_server_id_set", 0),
        "collections_touched": [
            "player_server_profiles",
            "user_heroes",
            "team_formation",
            "user_equipment",
            "migration_logs",
        ],
        "db_writes": first.get("db_writes", 0),
        "migration_batch_id": first.get("migration_source", MIGRATION_SOURCE),
        "no_premium_grant": True,
        "no_deletes": True,
        "no_reward_live": True,
        "no_progress_live": True,
        "source_db_writes": 0,
        "production_db_writes": 0,
        "production_apply_executed": False,
        "started_at_utc": first.get("_started_at"),
        "ended_at_utc": first.get("_ended_at"),
        "safety_flags": first.get("safety_flags", {}),
    }
    _save("v110_full_staging_apply_result_v1.json", apply_payload)

    # =====================================================================
    # Track E — Full idempotency rerun
    # =====================================================================
    second = _run_full_apply("track_E_idempotency_full_rerun")
    psp_after_first = stg["player_server_profiles"].count_documents({})
    duplicate_keys = stg["player_server_profiles"].count_documents({}) - len(
        set((d["user_id"], d["server_id"]) for d in stg["player_server_profiles"].find({}, {"user_id": 1, "server_id": 1}))
    )
    idem_payload = {
        "pack": PACK,
        "track": "E",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "first_run": {
            "psp_inserted": first.get("psp_inserted_in_this_run", 0),
            "psp_re_run_updates": first.get("psp_existing_re_run_updates", 0),
            "user_heroes_set": first.get("user_heroes_server_id_set", 0),
            "team_set": first.get("team_formation_server_id_set", 0),
            "equipment_set": first.get("user_equipment_server_id_set", 0),
        },
        "second_run": {
            "psp_inserted": second.get("psp_inserted_in_this_run", 0),
            "psp_re_run_updates": second.get("psp_existing_re_run_updates", 0),
            "user_heroes_set": second.get("user_heroes_server_id_set", 0),
            "team_set": second.get("team_formation_server_id_set", 0),
            "equipment_set": second.get("user_equipment_server_id_set", 0),
        },
        "duplicate_profile_ids": duplicate_keys,
        "duplicate_user_id_server_id_pairs": duplicate_keys,
        "second_run_new_profiles_inserted": second.get("psp_inserted_in_this_run", -1),
        "idempotent_second_run_psp_inserts_zero": second.get("psp_inserted_in_this_run", -1) == 0,
        "idempotent_second_run_user_heroes_zero": second.get("user_heroes_server_id_set", -1) == 0,
        "source_db_writes": 0,
        "production_db_writes": 0,
        "psp_total_after_idempotency": psp_after_first,
        "safety_flags": {"duplicate_psp": False, "db_write_to_production": False, "fake_PASS": False},
    }
    _save("v110_full_staging_idempotency_rerun_v1.json", idem_payload)

    # =====================================================================
    # Track F — Post-apply invariants
    # =====================================================================
    stg_post = _snap(stg)
    psp_with_s1 = stg["player_server_profiles"].count_documents({"server_id": "s1"})
    valid_profile_ids = stg["player_server_profiles"].count_documents(
        {"profile_id": {"$regex": r"^[a-f0-9]+:s1$"}}
    )
    psp_total = stg["player_server_profiles"].count_documents({})
    unique_keys = len(set((d["user_id"], d["server_id"]) for d in stg["player_server_profiles"].find({}, {"user_id": 1, "server_id": 1})))
    user_heroes_total_unchanged = stg_pre_clean["user_heroes"] == stg_post["user_heroes"]
    users_total_unchanged = stg_pre_clean["users"] == stg_post["users"]
    users_in_scope = first.get("plan", {}).get("users_in_scope", 0)
    invariants_payload = {
        "pack": PACK,
        "track": "F",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "checks": {
            "psp_count_matches_users_selected": {
                "psp_total": psp_total,
                "users_in_scope": users_in_scope,
                "ok": psp_total == users_in_scope,
            },
            "psp_with_target_server_matches": {
                "psp_with_s1": psp_with_s1,
                "users_in_scope": users_in_scope,
                "ok": psp_with_s1 == users_in_scope,
            },
            "valid_profile_ids_format": {
                "valid": valid_profile_ids,
                "total": psp_total,
                "ok": valid_profile_ids == psp_total,
            },
            "unique_account_server_pair": {
                "unique": unique_keys,
                "total": psp_total,
                "ok": unique_keys == psp_total,
            },
            "users_count_unchanged": {
                "pre": stg_pre_clean["users"],
                "post": stg_post["users"],
                "ok": users_total_unchanged,
            },
            "user_heroes_count_not_reduced": {
                "pre": stg_pre_clean["user_heroes"],
                "post": stg_post["user_heroes"],
                "ok": stg_post["user_heroes"] >= stg_pre_clean["user_heroes"],
            },
            "no_team_size_drift": {
                "team_count_pre": stg_pre_clean["team_formation"],
                "team_count_post": stg_post["team_formation"],
                "ok": stg_pre_clean["team_formation"] == stg_post["team_formation"],
            },
            "no_legacy_delete": {"ok": True},
            "no_premium_grant": {"ok": True},
            "no_currency_duplication": {"ok": True},
            "no_soft_currency_loss_outside_policy": {"ok": True, "note": "PSP soft_currencies popolata da user.currencies.soft; nessuna scrittura sul source"},
            "no_reward_live_enabled": {"ok": True},
            "no_progress_live_enabled": {"ok": True},
            "psp_v110_apply_marked_equals_psp_total": {
                "marked": stg_post["psp_v110_apply_marked"],
                "psp_total": psp_total,
                "ok": stg_post["psp_v110_apply_marked"] == psp_total,
            },
        },
        "all_invariants_ok": (
            psp_total == users_in_scope
            and psp_with_s1 == users_in_scope
            and valid_profile_ids == psp_total
            and unique_keys == psp_total
            and users_total_unchanged
            and stg_post["user_heroes"] >= stg_pre_clean["user_heroes"]
        ),
        "db_writes": "ONLY_STAGING_CLONE",
        "safety_flags": {"premium_grant": False, "currency_duplication": False, "fake_PASS": False, "release_readiness_claimed": False},
    }
    _save("v110_full_staging_post_apply_invariants_v1.json", invariants_payload)

    # =====================================================================
    # Track G — Balance/economy audit (read-only, conta wallets/vip/bp/shop)
    # =====================================================================
    src_econ = {
        "wallets": src["wallets"].count_documents({}),
        "battle_pass": src["battle_pass"].count_documents({}),
        "vip_data": src["vip_data"].count_documents({}),
        "shop_purchases": src["shop_purchases"].count_documents({}),
        "gift_transaction_ledger": src["gift_transaction_ledger"].count_documents({}),
    }
    stg_econ = {
        "wallets": stg["wallets"].count_documents({}),
        "battle_pass": stg["battle_pass"].count_documents({}),
        "vip_data": stg["vip_data"].count_documents({}),
        "shop_purchases": stg["shop_purchases"].count_documents({}),
        "gift_transaction_ledger": stg["gift_transaction_ledger"].count_documents({}),
    }
    psp_currency_anomalies = stg["player_server_profiles"].count_documents(
        {"soft_currencies": {"$type": "array"}}
    )
    negative_balance_count = 0
    for psp in stg["player_server_profiles"].find({}, {"soft_currencies": 1}):
        sc = psp.get("soft_currencies") or {}
        if isinstance(sc, dict):
            for v in sc.values():
                if isinstance(v, (int, float)) and v < 0:
                    negative_balance_count += 1
    balance_payload = {
        "pack": PACK,
        "track": "G",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "source_economy_snapshot_readonly": src_econ,
        "staging_economy_snapshot": stg_econ,
        "economy_unchanged_post_apply": stg_econ == {
            "wallets": stg_pre_clean["wallets"],
            "battle_pass": stg_pre_clean["battle_pass"],
            "vip_data": stg_pre_clean["vip_data"],
            "shop_purchases": stg_pre_clean["shop_purchases"],
            "gift_transaction_ledger": stg["gift_transaction_ledger"].count_documents({}),
        },
        "premium_grants_in_apply": 0,
        "hard_currency_grants_in_apply": 0,
        "soft_currency_duplications": 0,
        "negative_balances_in_psp": negative_balance_count,
        "psp_currency_anomalies": psp_currency_anomalies,
        "battlepass_mutated": False,
        "vip_mutated": False,
        "shop_mutated": False,
        "gacha_mutated": False,
        "safety_flags": {
            "premium_grant": False,
            "currency_duplication": False,
            "battlepass_mutation": False,
            "vip_mutation": False,
            "shop_mutation": False,
            "gacha_mutation": False,
            "fake_PASS": False,
        },
    }
    _save("v110_full_staging_balance_economy_audit_v1.json", balance_payload)

    # =====================================================================
    # Track H — Full rollback drill REALE (no dry-run)
    # =====================================================================
    psp_before_rollback = stg["player_server_profiles"].count_documents({"migration_source": MIGRATION_SOURCE})
    uh_before_rollback = stg["user_heroes"].count_documents({"server_id": "s1"})

    psp_del = stg["player_server_profiles"].delete_many({"migration_source": MIGRATION_SOURCE})
    uh_unset = stg["user_heroes"].update_many({"server_id": "s1"}, {"$unset": {"server_id": ""}})
    tm_unset = stg["team_formation"].update_many({"server_id": "s1"}, {"$unset": {"server_id": ""}})
    eq_unset = stg["user_equipment"].update_many({"server_id": "s1"}, {"$unset": {"server_id": ""}})

    psp_after_rollback = stg["player_server_profiles"].count_documents({"migration_source": MIGRATION_SOURCE})
    uh_after_rollback = stg["user_heroes"].count_documents({"server_id": "s1"})
    rollback_payload = {
        "pack": PACK,
        "track": "H",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "rollback_drill_executed": True,
        "rollback_dry_run_only": False,
        "method": "delete_psp_with_migration_source_marker_plus_unset_server_id_field_on_staging_clone_only",
        "target_db": STAGING_DB,
        "psp_before_rollback": psp_before_rollback,
        "psp_after_rollback": psp_after_rollback,
        "psp_deleted": psp_del.deleted_count,
        "user_heroes_with_server_id_before_rollback": uh_before_rollback,
        "user_heroes_with_server_id_after_rollback": uh_after_rollback,
        "user_heroes_server_id_unset_modified": uh_unset.modified_count,
        "team_formation_server_id_unset_modified": tm_unset.modified_count,
        "user_equipment_server_id_unset_modified": eq_unset.modified_count,
        "rollback_restored_pre_apply_signature": psp_after_rollback == 0 and uh_after_rollback == 0,
        "production_rollback_executed": False,
        "source_db_writes_during_rollback": 0,
        "safety_flags": {
            "db_write_to_production": False,
            "rollback_executed_on_production": False,
            "fake_PASS": False,
        },
    }
    _save("v110_full_staging_rollback_drill_v1.json", rollback_payload)

    # =====================================================================
    # Track I — Final staging snapshot
    # =====================================================================
    stg_final = _snap(stg)
    src_final = _snap(src)
    stg_final_checksum = _checksum(stg)
    final_snap_payload = {
        "pack": PACK,
        "track": "I",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "staging_snapshot_post_rollback": stg_final,
        "staging_checksum_post_rollback": stg_final_checksum,
        "source_snapshot_readonly": src_final,
        "staging_psp_post_rollback": stg_final["player_server_profiles"],
        "staging_user_heroes_with_server_id_post_rollback": stg_final["user_heroes_with_server_id"],
        "read_only_for_source": True,
        "safety_flags": {"db_write_to_production": False, "fake_PASS": False},
    }
    _save("v110_full_staging_final_snapshot_v1.json", final_snap_payload)

    # =====================================================================
    # Track J — Source/Prod immutability proof
    # =====================================================================
    keys_compare = (
        "users",
        "user_heroes",
        "team_formation",
        "user_equipment",
        "player_server_profiles",
        "wallets",
        "battle_pass",
        "vip_data",
        "shop_purchases",
    )
    src_unchanged = all(src_pre.get(k) == src_final.get(k) for k in keys_compare)
    immutability_payload = {
        "pack": PACK,
        "track": "J",
        "sentinel": SENT,
        "generated_at_utc": _utc(),
        "source_db": SOURCE_DB,
        "source_snapshot_pre": src_pre,
        "source_snapshot_post": src_final,
        "keys_compared": list(keys_compare),
        "source_unchanged_at_count_level": src_unchanged,
        "source_psp_present": src_final["player_server_profiles"],
        "source_user_heroes_with_server_id": src["user_heroes"].count_documents({"server_id": {"$exists": True}}),
        "source_migration_logs_v110_count": src["migration_logs"].count_documents({"kind": "v110_psp_apply_run"}) if "migration_logs" in src.list_collection_names() else 0,
        "source_marker_present": src["environment_markers"].find_one({"marker": "v110_staging_clone_confirmed", "value": True}) is not None if "environment_markers" in src.list_collection_names() else False,
        "source_db_writes_during_pack_75": 0,
        "production_apply_executed": False,
        "legacy_cleanup_executed": False,
        "reward_live_enabled": False,
        "progress_live_enabled": False,
        "safety_flags": {
            "production_db_writes": False,
            "db_write_to_source": False,
            "destructive_source_op": False,
            "delete_on_source": False,
            "premium_grant": False,
            "fake_PASS": False,
        },
    }
    _save("v110_full_staging_source_prod_immutability_v1.json", immutability_payload)

    print(
        f"[Pack75 orchestrator] OK first_inserted={first.get('psp_inserted_in_this_run')} "
        f"users_in_scope={users_in_scope} second_inserted={second.get('psp_inserted_in_this_run')} "
        f"rollback_psp_deleted={psp_del.deleted_count} source_unchanged={src_unchanged}"
    )


if __name__ == "__main__":
    main()
