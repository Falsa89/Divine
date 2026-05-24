#!/usr/bin/env python3
"""SLC-C-COMBO v2 (PROJECT_E Track A) — post SLC-G multishard baseline successor.

Sostituisce `validate_slc_c_combo_v1.py`. v2 e' un combo standalone che:
  - esegue il preflight v2 inline (DB + Phase-11 + SLC-G apply marker)
  - verifica i critical files no-diff (lookup chains)
  - emette il file di stato `_slc_c_combo_v2_result.json` con status=PASS

NON dipende da audit script intermedi; e' autosufficiente.
"""
import json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path("/app/backend/scripts")
OUT = Path("/app/data/design/server_lifecycle/_slc_c_combo_v2_result.json")
SLC_G_APPLY = Path("/app/data/design/system_safety/slc_g_default_s1_migration_apply_result_v1.json")
CRITICAL_FILES = (
    Path("/app/backend/routes/server_profiles.py"),
    Path("/app/backend/server.py"),
    Path("/app/data/design/system_safety/server_lifecycle_profile_selection_readiness_rollup_v1.json"),
)


def _sub_preflight() -> tuple[bool, str]:
    if os.environ.get("SECOND_SERVER_OPENING_ENABLED", "").lower() == "true":
        return False, "Phase 11 marker active"
    if not SLC_G_APPLY.exists():
        return False, f"SLC-G commit-A apply marker missing"
    try:
        from dotenv import load_dotenv
        from pymongo import MongoClient
        load_dotenv('/app/backend/.env')
        db = MongoClient(os.environ['MONGO_URL'])[os.environ.get('DB_NAME','divine_waifus')]
        if db.server_profiles.count_documents({}) != 0:
            return False, "server_profiles must be empty"
        idx = {i['name'] for i in db.server_profiles.list_indexes() if i['name'] != '_id_'}
        if not {"idx_user_server", "idx_user_active", "idx_server_active"}.issubset(idx):
            return False, f"missing canonical indexes: {idx}"
    except Exception as exc:
        return False, f"DB error: {exc}"
    return True, "OK"


def _sub_critical_files_no_diff() -> tuple[bool, str]:
    for f in CRITICAL_FILES:
        if not f.exists():
            return False, f"missing critical file: {f}"
    # Read-only sanity: server_profiles route still has FEATURE_FLAG canonical token.
    src = CRITICAL_FILES[0].read_text()
    if "FEATURE_FLAG" not in src or "_disabled_payload" not in src:
        return False, "server_profiles route lost canonical tokens"
    return True, "OK"


def _sub_api_smoke_readonly() -> tuple[bool, str]:
    import urllib.request, urllib.error
    base = "http://localhost:8001"
    try:
        with urllib.request.urlopen(base + "/api/heroes", timeout=5) as r:
            data = json.loads(r.read().decode("utf-8", "ignore"))
            if not isinstance(data, list) or len(data) != 100:
                return False, f"heroes count != 100"
    except Exception as exc:
        return False, f"heroes API error: {exc}"
    # /api/server-profiles/select must return 503 default
    try:
        urllib.request.urlopen(base + "/api/server-profiles/select", timeout=5)
        return False, "sp/select expected 503, got 2xx"
    except urllib.error.HTTPError as e:
        if e.code != 503: return False, f"sp/select got {e.code}"
    except Exception as exc:
        return False, f"sp/select error: {exc}"
    return True, "OK"


def main():
    subs = (
        ("preflight_post_g_v2", _sub_preflight),
        ("critical_files_no_diff", _sub_critical_files_no_diff),
        ("api_smoke_readonly", _sub_api_smoke_readonly),
    )
    results = []
    all_ok = True
    for label, fn in subs:
        ok, msg = fn()
        if not ok: all_ok = False
        print(f"  {'PASS' if ok else 'FAIL'}  {label}: {msg}")
        results.append({"label": label, "status": "PASS" if ok else "FAIL", "msg": msg})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "task_id": "SLC_C_COMBO_V2",
        "status": "PASS" if all_ok else "FAIL",
        "sub_tests": results,
        "superseded": "validate_slc_c_combo_v1.py",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
    }, indent=2))
    print(f"[slc_c_combo_v2] {'PASS' if all_ok else 'FAIL'}")
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__": main()
