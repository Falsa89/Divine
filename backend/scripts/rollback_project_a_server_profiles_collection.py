#!/usr/bin/env python3
"""
PROJECT_A Track A rollback (gated, idempotent).

Droppa la collezione server_profiles e i suoi 3 indici canonici creati da
Track A. Safe solo se la collezione contiene 0 documenti (empty drop).

Gated da PROJECT_A_TRACK_A_ROLLBACK=YES. Non eseguito automaticamente.

Usage:
  PROJECT_A_TRACK_A_ROLLBACK=YES python3 \\
    /app/backend/scripts/rollback_project_a_server_profiles_collection.py

Exit 0 OK / 1 FAIL.
"""
import json
import os
import sys

GATE_ENV = "PROJECT_A_TRACK_A_ROLLBACK"
GATE_OK = "YES"
ROLLBACK_ID = "project_a_track_a_server_profiles_collection"


def main() -> None:
    if os.environ.get(GATE_ENV) != GATE_OK:
        print(f"[GATED] rollback {ROLLBACK_ID} NOT executed. Set {GATE_ENV}={GATE_OK} to proceed.")
        sys.exit(0)

    try:
        from dotenv import load_dotenv
        load_dotenv('/app/backend/.env')
        from pymongo import MongoClient
    except Exception as exc:
        print(f"[FAIL] missing deps: {exc}")
        sys.exit(1)

    url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'divine_db')
    client = MongoClient(url)
    db = client[db_name]

    cols = db.list_collection_names()
    if "server_profiles" not in cols:
        print(f"[OK] rollback {ROLLBACK_ID} no-op: server_profiles already absent")
        sys.exit(0)

    doc_count = db.server_profiles.count_documents({})
    if doc_count != 0:
        print(f"[FAIL] rollback ABORTED: server_profiles contains {doc_count} doc(s); drop not safe. Manual review required.")
        sys.exit(1)

    indexes_pre = sorted({i["name"] for i in db.server_profiles.list_indexes()})
    db.server_profiles.drop_indexes()
    db.drop_collection("server_profiles")
    cols_post = db.list_collection_names()

    print(f"[OK] rollback {ROLLBACK_ID} applied: dropped server_profiles (empty) + indexes {indexes_pre}")
    print(json.dumps({
        "status": "ROLLED_BACK",
        "collections_post": len(cols_post),
        "server_profiles_present": "server_profiles" in cols_post,
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
