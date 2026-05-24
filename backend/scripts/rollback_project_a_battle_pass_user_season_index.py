#!/usr/bin/env python3
"""
PROJECT_A Track B rollback (gated, idempotent).

Droppa l'indice idx_battle_pass_user_season da battle_pass.
Non tocca i documenti.

Gated da PROJECT_A_TRACK_B_ROLLBACK=YES.

Exit 0 OK / 1 FAIL.
"""
import json
import os
import sys

GATE_ENV = "PROJECT_A_TRACK_B_ROLLBACK"
GATE_OK = "YES"
INDEX_NAME = "idx_battle_pass_user_season"
ROLLBACK_ID = "project_a_track_b_battle_pass_user_season_index"


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
    db = MongoClient(url)[db_name]

    existing = {i["name"] for i in db.battle_pass.list_indexes()}
    if INDEX_NAME not in existing:
        print(f"[OK] rollback {ROLLBACK_ID} no-op: {INDEX_NAME} already absent")
        sys.exit(0)

    db.battle_pass.drop_index(INDEX_NAME)
    post = {i["name"] for i in db.battle_pass.list_indexes()}
    print(f"[OK] rollback {ROLLBACK_ID} applied: dropped {INDEX_NAME}")
    print(json.dumps({"status": "ROLLED_BACK", "battle_pass_indexes_post": sorted(post)}))
    sys.exit(0)


if __name__ == "__main__":
    main()
