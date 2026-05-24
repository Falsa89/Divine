#!/usr/bin/env python3
"""PROJECT_C Track A validator (HTTP smoke + source check)."""
import json, os, sys, urllib.request, urllib.error
from pathlib import Path

RESULT = Path("/app/data/design/server_lifecycle/project_c_server_profiles_dual_route_behavior_result_v1.json")
MODULE = Path("/app/backend/routes/server_profiles.py")
BASE = "http://localhost:8001"


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def _http(method, path):
    req = urllib.request.Request(BASE + path, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, r.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        try: body = e.read().decode("utf-8", "ignore")
        except Exception: body = ""
        return e.code, body
    except Exception as exc:
        return -1, str(exc)


def main():
    if not RESULT.exists(): fail(f"missing {RESULT}")
    m = json.loads(RESULT.read_text())
    if m.get("verdict") != "TRACK_A_SERVER_PROFILES_DUAL_ROUTE_BEHAVIOR_APPLIED_FLAG_OFF":
        fail(f"verdict mismatch: {m.get('verdict')}")
    if m.get("db_writes_executed") != 0: fail("db_writes_executed must be 0")
    if m.get("users_server_field_mutated") is not False: fail("users_server_field_mutated must be False")
    if m.get("dual_write_db_behavior") is not False: fail("dual_write_db_behavior must be False")
    if m.get("active_server_switching_executed") is not False: fail("active_server_switching_executed must be False")

    if not MODULE.exists(): fail("module missing")
    src = MODULE.read_text()
    for n in ("_read_only_select_response_for_user", "PROJECT_C_TRACK_A_BEHAVIOR_LAYER",
              "mutation_executed", "active_server_switched", "dual_write_executed",
              "SERVER_PROFILES_RUNTIME_ENABLED"):
        if n not in src: fail(f"module missing token: {n}")

    # Feature flag must be unset in live env.
    if os.environ.get("SERVER_PROFILES_RUNTIME_ENABLED", "").lower() == "true":
        fail("SERVER_PROFILES_RUNTIME_ENABLED must remain unset/false in live env")

    # HTTP live: default 503 preserved.
    code, body = _http("GET", "/api/server-profiles/select")
    if code != 503 or "disabled" not in body:
        fail(f"GET sp/select expected 503+disabled, got {code} body={body[:200]}")
    code, body = _http("POST", "/api/server-profiles/select")
    if code != 503 or "disabled" not in body:
        fail(f"POST sp/select expected 503+disabled, got {code} body={body[:200]}")
    code, body = _http("GET", "/api/heroes")
    if code != 200 or len(json.loads(body)) != 100:
        fail("heroes=100 invariant violated")

    # DB invariants.
    try:
        from dotenv import load_dotenv
        from pymongo import MongoClient
        load_dotenv('/app/backend/.env')
        db = MongoClient(os.environ['MONGO_URL'])[os.environ.get('DB_NAME','divine_waifus')]
        sp_count = db.server_profiles.count_documents({})
        if sp_count != 0: fail(f"server_profiles must remain empty, got {sp_count}")
    except Exception as exc:
        fail(f"live DB check error: {exc}")

    print("[PASS] PROJECT_C Track A behavior layer OK: helpers present; flag unset; live default 503; DB still empty; heroes=100")
    sys.exit(0)

if __name__ == "__main__": main()
