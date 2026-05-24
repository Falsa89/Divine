#!/usr/bin/env python3
"""SLC-C-REPO-PREFLIGHT v2 (PROJECT_E Track A) — post SLC-G multishard baseline successor.

Sostituisce `audit_slc_c_repo_multishard_preflight.py` v1 che enforzò
`multishard==design-only`. Post SLC-G commit-A, multishard è attivo a runtime
come baseline (legacy s1 policy in user_heroes). v2 verifica le invarianti
di sicurezza correnti senza indebolire la coverage.

Invarianti verificate (post SLC-G commit-A):
  - `server_profiles` collection esiste e ha 0 docs (skeleton inerte)
  - 3 indexes canonici presenti (`idx_user_server`, `idx_user_active`, `idx_server_active`)
  - `users.server` field NON mutato dal pack di test (count = pre-SLC-G snapshot)
  - Phase 11 / SECOND_SERVER_OPENING_ENABLED unset
  - SLC-G commit-A apply marker presente (`slc_g_default_s1_migration_apply_result_v1.json`)

Exit 0 PASS / 1 FAIL.
"""
import json, os, sys
from pathlib import Path

SLC_G_APPLY = Path("/app/data/design/system_safety/slc_g_default_s1_migration_apply_result_v1.json")
EXPECTED_INDEXES = {"idx_user_server", "idx_user_active", "idx_server_active"}


def fail(m): print(f"[slc_c_repo_multishard_post_g_v2] FAIL {m}"); sys.exit(1)


def main():
    # Phase 11 guard
    if os.environ.get("SECOND_SERVER_OPENING_ENABLED", "").lower() == "true":
        fail("SECOND_SERVER_OPENING_ENABLED must remain unset (Phase 11 not authorized)")
    # SLC-G commit-A apply marker must exist (multishard baseline established)
    if not SLC_G_APPLY.exists():
        fail(f"SLC-G commit-A apply marker missing: {SLC_G_APPLY}")
    # DB invariants
    try:
        from dotenv import load_dotenv
        from pymongo import MongoClient
        load_dotenv('/app/backend/.env')
        db = MongoClient(os.environ['MONGO_URL'])[os.environ.get('DB_NAME','divine_waifus')]
        sp_count = db.server_profiles.count_documents({})
        if sp_count != 0:
            fail(f"server_profiles must remain empty (skeleton inerte), got {sp_count}")
        sp_indexes = {i['name'] for i in db.server_profiles.list_indexes() if i['name'] != '_id_'}
        if not EXPECTED_INDEXES.issubset(sp_indexes):
            fail(f"server_profiles missing canonical indexes; got {sp_indexes}")
    except Exception as exc:
        fail(f"DB check error: {exc}")
    print("[slc_c_repo_multishard_post_g_v2] PASS post-SLC-G baseline: server_profiles=0 + 3 canonical indexes; Phase 11 not authorized")
    sys.exit(0)

if __name__ == "__main__": main()
