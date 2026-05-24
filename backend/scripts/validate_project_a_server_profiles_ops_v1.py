#!/usr/bin/env python3
"""
PROJECT_A Track A validator (read-only; uses pymongo to verify state).

Verifica live:
- server_profiles collection esiste
- 3 indici canonical presenti con nomi attesi
- idx_user_server e' unique
- 0 documenti nella collection (inert)
- nessun feature flag SERVER_PROFILES_RUNTIME_ENABLED attivato

Legge anche il result JSON e verifica integrita'.

Exit 0 PASS / 1 FAIL.
"""
import json
import os
import sys
from pathlib import Path

RESULT = Path("/app/data/design/server_lifecycle/project_a_server_profiles_ops_result_v1.json")
EXPECTED_INDEXES = {"idx_user_server", "idx_user_active", "idx_server_active"}


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not RESULT.exists():
        fail(f"missing result: {RESULT}")
    m = json.loads(RESULT.read_text(encoding="utf-8"))
    if m.get("verdict") != "TRACK_A_SERVER_PROFILES_COLLECTION_APPLIED_SAFE":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("db_collection_created") is not True:
        fail("db_collection_created must be True")
    if m.get("db_indexes_created") != 3:
        fail("db_indexes_created must be 3")
    if m.get("db_data_rows_written") != 0:
        fail("db_data_rows_written must be 0")
    if m.get("runtime_state", {}).get("runtime_enabled") is not False:
        fail("runtime_state.runtime_enabled must be False")
    if m.get("runtime_state", {}).get("endpoint_exposed") is not False:
        fail("runtime_state.endpoint_exposed must be False")

    try:
        from dotenv import load_dotenv
        load_dotenv('/app/backend/.env')
        from pymongo import MongoClient
    except Exception as exc:
        fail(f"missing deps for live check: {exc}")

    url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'divine_db')
    db = MongoClient(url)[db_name]

    if "server_profiles" not in db.list_collection_names():
        fail("server_profiles collection MISSING in live DB")

    idx_info = list(db.server_profiles.list_indexes())
    idx_names = {i["name"] for i in idx_info}
    for expected in EXPECTED_INDEXES:
        if expected not in idx_names:
            fail(f"missing index in live DB: {expected}")

    unique_idx = next((i for i in idx_info if i["name"] == "idx_user_server"), None)
    if not unique_idx or not unique_idx.get("unique"):
        fail("idx_user_server must be unique in live DB")

    doc_count = db.server_profiles.count_documents({})
    if doc_count != 0:
        fail(f"server_profiles must be empty (inert), got {doc_count} docs")

    # Feature flag must remain unset.
    if os.environ.get("SERVER_PROFILES_RUNTIME_ENABLED"):
        fail("SERVER_PROFILES_RUNTIME_ENABLED must remain unset (no runtime activation)")

    print("[PASS] PROJECT_A Track A live state OK: server_profiles + 3 canonical indexes (unique on idx_user_server); 0 docs; runtime UNSET")
    sys.exit(0)


if __name__ == "__main__":
    main()
