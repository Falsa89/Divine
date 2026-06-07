#!/usr/bin/env python3
"""v110 environment classification - read-only DB inspection.

Labels:
  STAGING_CLONE_CONFIRMED       - explicit staging marker collection found
  LOCAL_CONTAINER_NON_PROD      - localhost MongoDB, no production markers, no staging marker
  PRODUCTION_OR_UNSAFE          - mongodb+srv, prod hint in URI/DBNAME, or explicit prod marker
  UNKNOWN                       - cannot reach DB or insufficient evidence

Never writes DB. Produces JSON.
"""
import json, os, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "data/design/v110_psp_apply_staging_smoke/v110_environment_classification_v1.json")


def _try_db():
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(ROOT, "backend", ".env"))
    except Exception:
        pass
    try:
        from pymongo import MongoClient
        url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
        name = os.environ.get("DB_NAME", "divine_waifus")
        client = MongoClient(url, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        return client[name], url, name
    except Exception as e:
        return None, os.environ.get("MONGO_URL", ""), os.environ.get("DB_NAME", "")


def main():
    db, url, name = _try_db()
    is_srv = url.startswith("mongodb+srv://")
    is_localhost = ("localhost" in url) or ("127.0.0.1" in url)
    name_lower = name.lower()
    prod_in_name = "prod" in name_lower and "divine_waifus" not in name_lower
    prod_in_url = "prod" in url.lower() and "localhost" not in url
    staging_in_name = "staging" in name_lower or "clone" in name_lower

    staging_marker_doc = None
    prod_marker_doc = None
    if db is not None:
        try:
            staging_marker_doc = db["environment_markers"].find_one({"marker": "v110_staging_clone_confirmed", "value": True})
        except Exception:
            staging_marker_doc = None
        try:
            prod_marker_doc = db["environment_markers"].find_one({"marker": "production", "value": True})
        except Exception:
            prod_marker_doc = None

    if db is None:
        classification = "UNKNOWN"
        reason = "mongo_unreachable"
    elif prod_marker_doc is not None or prod_in_name or prod_in_url:
        classification = "PRODUCTION_OR_UNSAFE"
        reason = "prod_marker_or_prod_hint_in_uri_or_dbname"
    elif is_srv and not staging_in_name and staging_marker_doc is None:
        classification = "PRODUCTION_OR_UNSAFE"
        reason = "mongodb_srv_cluster_without_staging_evidence"
    elif staging_marker_doc is not None or staging_in_name:
        classification = "STAGING_CLONE_CONFIRMED"
        reason = "explicit_staging_marker_or_dbname"
    elif is_localhost:
        classification = "LOCAL_CONTAINER_NON_PROD"
        reason = "localhost_mongo_dev_container_no_staging_marker"
    else:
        classification = "UNKNOWN"
        reason = "insufficient_evidence"

    safe_to_apply = classification == "STAGING_CLONE_CONFIRMED"

    payload = {
        "pack": "MEGA_RELEASE_ACCELERATION_72_v110_PSP_APPLY_STAGING_SMOKE_LIMITED",
        "track": "B",
        "sentinel": "PUBLIC_SYNC_TAG_v110_PSP_APPLY_STAGING_SMOKE_LIMITED",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "classification": classification,
        "reason": reason,
        "safe_to_apply": safe_to_apply,
        "signals": {
            "mongo_url_kind": "srv" if is_srv else ("localhost" if is_localhost else "other"),
            "mongo_url_redacted": (url.split("@")[-1] if "@" in url else url),
            "db_name": name,
            "prod_hint_in_name": prod_in_name,
            "prod_hint_in_url": prod_in_url,
            "staging_hint_in_name": staging_in_name,
            "staging_marker_doc_found": staging_marker_doc is not None,
            "production_marker_doc_found": prod_marker_doc is not None,
            "mongo_reachable": db is not None,
        },
        "db_writes": 0,
        "safety_flags": {
            "production_db_smoke": False,
            "fake_PASS": False,
            "release_readiness_claimed": False,
        },
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(payload, open(OUT, "w"), indent=2, ensure_ascii=False)
    print(f"[v110 ENV CLASSIFICATION] {classification} reason={reason} safe_to_apply={safe_to_apply}")
    sys.exit(0)


if __name__ == "__main__":
    main()
