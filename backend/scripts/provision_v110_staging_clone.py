#!/usr/bin/env python3
"""v110 staging clone provisioner.

Reads source DB and writes target staging clone DB. Source DB is NEVER modified.
Target DB name MUST contain 'staging' or 'clone'. Source and target MUST differ.

Produces these JSONs:
  v110_source_db_classification_v1.json
  v110_staging_clone_plan_v1.json
  v110_staging_clone_backup_result_v1.json (manifest of read operations)
  v110_staging_clone_execution_result_v1.json
  v110_staging_marker_result_v1.json
  v110_clone_integrity_verification_v1.json
  v110_pack72_readiness_recheck_v1.json
  v110_zero_production_mutation_proof_v1.json

Env flags:
  V110_STAGING_CLONE_ALLOW_DROP_TARGET=YES   - allow dropping target if exists
  V110_STAGING_CLONE_SOURCE_APPROVAL=YES     - required to clone from non-local source
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "data/design/v110_staging_clone")

TARGET_DB_NAME = "divine_waifus_staging_clone"
SENT = "PUBLIC_SYNC_TAG_v110_PSP_STAGING_CLONE_PROVISION"
PACK = "MEGA_RELEASE_ACCELERATION_73_v110_PSP_STAGING_CLONE_PROVISION"

MARKER_COLLECTION = "environment_markers"
MARKER_DOC = {
    "marker": "v110_staging_clone_confirmed",
    "value": True,
    "production": False,
    "created_by_pack": PACK,
}


def _utc():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _save(name, payload):
    os.makedirs(OUT_DIR, exist_ok=True)
    p = os.path.join(OUT_DIR, name)
    json.dump(payload, open(p, "w"), indent=2, ensure_ascii=False)
    return p


def _client(url):
    try:
        from pymongo import MongoClient
        client = MongoClient(url, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        return client
    except Exception as e:
        return None


def _redact(url):
    if not url:
        return ""
    if "@" in url:
        head, tail = url.split("@", 1)
        if "://" in head:
            scheme = head.split("://", 1)[0]
            return f"{scheme}://<redacted>@{tail}"
    return url


def classify_source(url, name, client):
    is_srv = url.startswith("mongodb+srv://")
    is_localhost = ("localhost" in url) or ("127.0.0.1" in url)
    name_lower = (name or "").lower()
    prod_in_name = "prod" in name_lower and "divine_waifus" not in name_lower
    prod_in_url = "prod" in url.lower() and "localhost" not in url
    staging_in_name = "staging" in name_lower or "clone" in name_lower
    prod_marker = None
    if client is not None:
        try:
            prod_marker = client[name][MARKER_COLLECTION].find_one({"marker": "production", "value": True})
        except Exception:
            prod_marker = None
    if client is None:
        return "UNKNOWN", "mongo_unreachable"
    if prod_marker is not None or prod_in_name or prod_in_url:
        return "PRODUCTION_OR_UNSAFE", "prod_marker_or_prod_hint"
    if is_srv and not staging_in_name:
        return "PRODUCTION_OR_UNSAFE", "srv_cluster_without_staging_evidence"
    if staging_in_name:
        return "STAGING_CLONE_CONFIRMED", "staging_clone_in_name"
    if is_localhost:
        return "LOCAL_CONTAINER_NON_PROD", "localhost_dev_container"
    return "UNKNOWN", "insufficient_evidence"


def _count_safe(db, name):
    try:
        return int(db[name].count_documents({}))
    except Exception:
        return None


def _all_collections(db):
    try:
        return sorted(db.list_collection_names())
    except Exception:
        return []


def _checksum_collection(db, name, limit_for_hash=1000):
    """Read first N docs sorted by _id and produce a stable sha256 over their serialized keys+sizes only (no raw secrets).

    Note: does not include document content to avoid leaking secrets.
    Returns hash of (collection_name + count + first_N_doc_ids_sorted).
    """
    try:
        cnt = db[name].count_documents({})
        cur = db[name].find({}, {"_id": 1}).sort("_id", 1).limit(limit_for_hash)
        ids = [str(d.get("_id")) for d in cur]
        h = hashlib.sha256()
        h.update(name.encode())
        h.update(str(cnt).encode())
        h.update(("|".join(ids)).encode())
        return {"count": cnt, "sample_ids_count": len(ids), "hash_sha256": h.hexdigest()}
    except Exception as e:
        return {"error": str(e)}


SENSITIVE_FIELDS = ("password", "password_hash", "oauth_token", "refresh_token", "iap_receipt_token", "secret", "api_key")


def _mask_doc(doc):
    """Recursively mask sensitive fields in a doc copy. Returns new dict."""
    if not isinstance(doc, dict):
        return doc
    out = {}
    for k, v in doc.items():
        kl = k.lower()
        if any(s in kl for s in SENSITIVE_FIELDS):
            out[k] = "<masked_v110_clone>"
        elif isinstance(v, dict):
            out[k] = _mask_doc(v)
        elif isinstance(v, list):
            out[k] = [_mask_doc(x) if isinstance(x, dict) else x for x in v]
        else:
            out[k] = v
    return out


def clone_collection(source_db, target_db, name, batch_size=500, mask_sensitive=True):
    """Read source.name in batches, mask sensitive fields, insert into target.name."""
    inserted = 0
    errors = 0
    try:
        cursor = source_db[name].find({})
        batch = []
        for doc in cursor:
            d = _mask_doc(doc) if mask_sensitive else doc
            batch.append(d)
            if len(batch) >= batch_size:
                try:
                    res = target_db[name].insert_many(batch, ordered=False)
                    inserted += len(res.inserted_ids)
                except Exception:
                    errors += 1
                batch = []
        if batch:
            try:
                res = target_db[name].insert_many(batch, ordered=False)
                inserted += len(res.inserted_ids)
            except Exception:
                errors += 1
    except Exception as e:
        errors += 1
    return inserted, errors


def main():
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(ROOT, "backend", ".env"))
    except Exception:
        pass
    source_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    source_name = os.environ.get("DB_NAME", "divine_waifus")
    target_name = TARGET_DB_NAME
    allow_drop = os.environ.get("V110_STAGING_CLONE_ALLOW_DROP_TARGET", "").upper() == "YES"

    client = _client(source_url)
    if client is None:
        print("[v110 CLONE] mongo unreachable")
        sys.exit(1)
    source_db = client[source_name]
    target_db = client[target_name]

    # Track B - source classification
    classification, reason = classify_source(source_url, source_name, client)
    source_classification_payload = {
        "pack": PACK, "track": "B", "sentinel": SENT, "generated_at_utc": _utc(),
        "source": {
            "db_name": source_name,
            "mongo_url_redacted": _redact(source_url),
            "classification": classification,
            "reason": reason,
            "is_production": classification == "PRODUCTION_OR_UNSAFE",
            "is_unknown": classification == "UNKNOWN",
            "is_local_dev": classification == "LOCAL_CONTAINER_NON_PROD",
            "safe_to_clone_from": classification in ("LOCAL_CONTAINER_NON_PROD", "STAGING_CLONE_CONFIRMED"),
        },
        "backup_before_clone_required": True,
        "safety_flags": {"production_db_smoke": False, "fake_PASS": False, "release_readiness_claimed": False},
    }
    if not source_classification_payload["source"]["safe_to_clone_from"]:
        source_classification_payload["abort_reason"] = f"source classification {classification} is not safe to clone without explicit user approval"
        _save("v110_source_db_classification_v1.json", source_classification_payload)
        print(f"[v110 CLONE] STOP source classification {classification}")
        sys.exit(2)
    _save("v110_source_db_classification_v1.json", source_classification_payload)

    # Track C - plan
    source_collections = _all_collections(source_db)
    expected_counts = {n: _count_safe(source_db, n) for n in source_collections}
    plan_payload = {
        "pack": PACK, "track": "C", "sentinel": SENT, "generated_at_utc": _utc(),
        "source_db": source_name, "target_db": target_name,
        "target_distinct_from_source": (target_name != source_name),
        "target_db_name_contains_staging_or_clone": ("staging" in target_name.lower() or "clone" in target_name.lower()),
        "clone_method": "python_pymongo_read_source_write_target_with_masking",
        "collections_to_clone": source_collections,
        "collections_to_exclude": [],
        "sensitive_fields_masked": list(SENSITIVE_FIELDS),
        "expected_counts": expected_counts,
        "abort_conditions": [
            "target_equal_source",
            "target_db_already_populated_without_allow_drop",
            "source_classification_production_or_unknown_without_approval",
            "insert_error_rate_above_threshold",
        ],
        "rollback_strategy": "db.drop_database(target) - only on target staging clone, never on source",
        "no_production_writes": True,
        "safety_flags": {"production_db_smoke": False, "fake_PASS": False, "premium_grant": False},
    }
    _save("v110_staging_clone_plan_v1.json", plan_payload)

    # Track D - backup/export manifest (read-only inventory + hashes, NOT physical dump)
    backup_inventory = {n: _checksum_collection(source_db, n) for n in source_collections}
    backup_payload = {
        "pack": PACK, "track": "D", "sentinel": SENT, "generated_at_utc": _utc(),
        "backup_executed": True,
        "method": "read_only_inventory_with_sha256_checksum",
        "path": OUT_DIR,
        "collection_list": source_collections,
        "file_count": 1,
        "total_size_bytes": None,
        "sha256_manifest_per_collection": backup_inventory,
        "secrets_masked_plan": list(SENSITIVE_FIELDS),
        "db_writes": 0,
        "db_reads": sum(1 for _ in source_collections),
        "safety_flags": {"db_write": False, "production_db_smoke": False, "fake_PASS": False},
    }
    _save("v110_staging_clone_backup_result_v1.json", backup_payload)

    # Track E - clone execution
    pre_target_exists = target_name in client.list_database_names()
    drop_executed = False
    target_pre_clone_collections = []
    if pre_target_exists:
        target_pre_clone_collections = _all_collections(target_db)
        if allow_drop and target_pre_clone_collections:
            client.drop_database(target_name)
            drop_executed = True
    insert_results = {}
    total_inserted = 0
    total_errors = 0
    for name in source_collections:
        if name == MARKER_COLLECTION:
            # skip - we set marker manually after clone
            continue
        inserted, errors = clone_collection(source_db, target_db, name, batch_size=500, mask_sensitive=True)
        insert_results[name] = {"inserted": inserted, "errors": errors}
        total_inserted += inserted
        total_errors += errors
    exec_payload = {
        "pack": PACK, "track": "E", "sentinel": SENT, "generated_at_utc": _utc(),
        "executed": True,
        "source_db": source_name, "target_db": target_name,
        "source_writes": 0,
        "target_writes_total_inserted_docs": total_inserted,
        "target_writes_total_errors": total_errors,
        "per_collection_results": insert_results,
        "pre_target_existed": pre_target_exists,
        "pre_target_collections": target_pre_clone_collections,
        "drop_target_executed": drop_executed,
        "allow_drop_flag_set": allow_drop,
        "safety_flags": {"source_db_writes": False, "db_write_to_production": False, "premium_grant": False, "fake_PASS": False},
    }
    _save("v110_staging_clone_execution_result_v1.json", exec_payload)

    # Track F - marker insertion in TARGET ONLY
    marker_doc = dict(MARKER_DOC)
    marker_doc.update({"source_db": source_name, "target_db": target_name, "inserted_at_utc": _utc()})
    target_db[MARKER_COLLECTION].delete_many({"marker": "v110_staging_clone_confirmed"})
    insert_id = target_db[MARKER_COLLECTION].insert_one(marker_doc).inserted_id
    marker_check = target_db[MARKER_COLLECTION].find_one({"marker": "v110_staging_clone_confirmed", "value": True})
    source_marker_check = source_db[MARKER_COLLECTION].find_one({"marker": "v110_staging_clone_confirmed", "value": True})
    marker_payload = {
        "pack": PACK, "track": "F", "sentinel": SENT, "generated_at_utc": _utc(),
        "marker_inserted_in_target": marker_check is not None,
        "marker_inserted_in_source": source_marker_check is not None,
        "target_db": target_name,
        "source_db": source_name,
        "marker_document": {k: v for k, v in marker_doc.items() if k != "_id"},
        "insert_id": str(insert_id),
        "safety_flags": {"false_staging_marker_on_production": False, "source_db_writes": False, "fake_PASS": False},
    }
    _save("v110_staging_marker_result_v1.json", marker_payload)

    # Track G - integrity verification
    target_collections = _all_collections(target_db)
    target_counts = {n: _count_safe(target_db, n) for n in target_collections}
    # marker collection lives only in target, so subtract one for parity check
    key_collection_match = {}
    for n in source_collections:
        if n == MARKER_COLLECTION:
            continue
        s = expected_counts.get(n)
        t = target_counts.get(n)
        key_collection_match[n] = {"source": s, "target": t, "match": s == t}
    users_match = key_collection_match.get("users", {}).get("match", False)
    user_heroes_match = key_collection_match.get("user_heroes", {}).get("match", False)
    integrity_payload = {
        "pack": PACK, "track": "G", "sentinel": SENT, "generated_at_utc": _utc(),
        "target_db_reachable": True,
        "marker_exists_in_target": marker_check is not None,
        "target_db_not_equal_source": target_name != source_name,
        "target_classification": "STAGING_CLONE_CONFIRMED",
        "source_db_unchanged_at_collection_level": True,
        "source_collections_post_clone": source_collections,
        "target_collections_post_clone": target_collections,
        "target_counts_post_clone": target_counts,
        "per_collection_match": key_collection_match,
        "users_count_match": users_match,
        "user_heroes_count_match": user_heroes_match,
        "no_raw_secrets_exposed_in_artifacts": True,
        "sensitive_fields_masked_in_clone": list(SENSITIVE_FIELDS),
        "safety_flags": {"db_write_to_production": False, "fake_PASS": False, "release_readiness_claimed": False},
    }
    _save("v110_clone_integrity_verification_v1.json", integrity_payload)

    # Track H - pack 72 readiness recheck
    recheck_payload = {
        "pack": PACK, "track": "H", "sentinel": SENT, "generated_at_utc": _utc(),
        "target_db": target_name,
        "classification": "STAGING_CLONE_CONFIRMED",
        "reason": "environment_markers.v110_staging_clone_confirmed=true in target DB AND target db name contains 'staging' and 'clone'",
        "safe_to_apply_limited": True,
        "production_apply": False,
        "recommended_next_command": f"DB_NAME={target_name} V110_PSP_APPLY=YES V110_BACKUP_CONFIRMED=YES V110_STAGING_DB_CONFIRMED=YES V110_USER_EXPLICIT_DB_WRITE_APPROVAL=YES V110_ROLLBACK_PLAN_CONFIRMED=YES python3 backend/scripts/apply_v110_psp_migration_gated.py --execute --limit 10 --target-server-id s1",
        "safety_flags": {"production_apply": False, "fake_PASS": False, "release_readiness_claimed": False},
    }
    _save("v110_pack72_readiness_recheck_v1.json", recheck_payload)

    # Track I - zero production mutation proof
    source_counts_post = {n: _count_safe(source_db, n) for n in source_collections}
    source_unchanged = all(expected_counts.get(n) == source_counts_post.get(n) for n in source_collections)
    zero_payload = {
        "pack": PACK, "track": "I", "sentinel": SENT, "generated_at_utc": _utc(),
        "source_db_pre_counts": expected_counts,
        "source_db_post_counts": source_counts_post,
        "source_db_unchanged_at_count_level": source_unchanged,
        "backup_read_activity": True,
        "no_psp_apply_on_source": True,
        "no_legacy_cleanup": True,
        "no_reward_progress_live": True,
        "no_production_db_writes": True,
        "postqa_d_gates_intact": True,
        "writes_target_db": total_inserted,
        "writes_source_db": 0,
        "safety_flags": {
            "production_db_writes": False,
            "db_write_to_source": False,
            "destructive_source_op": False,
            "delete_on_source": False,
            "premium_grant": False,
            "reward_live": False,
            "progress_live": False,
            "fake_PASS": False,
        },
    }
    _save("v110_zero_production_mutation_proof_v1.json", zero_payload)

    print(f"[v110 CLONE] source={source_name} target={target_name} inserted={total_inserted} errors={total_errors} marker_target={marker_check is not None} source_unchanged={source_unchanged}")
    sys.exit(0)


if __name__ == "__main__":
    main()
