#!/usr/bin/env python3
"""PROJECT_D Track A validator (HTTP smoke + source + unit-style preview helper)."""
import json, os, sys, urllib.request, urllib.error
from pathlib import Path

RESULT = Path("/app/data/design/server_lifecycle/project_d_server_profiles_flagged_preview_result_v1.json")
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
    if m.get("verdict") != "TRACK_A_SERVER_PROFILES_FLAGGED_PREVIEW_APPLIED_INERT":
        fail(f"verdict mismatch: {m.get('verdict')}")
    if m.get("default_route_behavior_changed") is not False: fail("default_route_behavior_changed must be False")
    if m.get("db_writes_executed") != 0: fail("db_writes_executed must be 0")
    if m.get("users_server_field_mutated") is not False: fail("users_server_field_mutated must be False")
    if m.get("dual_write_db_behavior") is not False: fail("dual_write_db_behavior must be False")
    if m.get("active_server_switching_executed") is not False: fail("active_server_switching_executed must be False")
    if m.get("second_server_opened") is not False: fail("second_server_opened must be False")

    if not MODULE.exists(): fail("module missing")
    src = MODULE.read_text()
    for n in ("_preview_runtime_enabled", "_preview_dry_run_envelope",
              "PREVIEW_FEATURE_FLAG", "SERVER_PROFILES_PREVIEW_ENABLED",
              "PROJECT_D_TRACK_A_FLAGGED_PREVIEW_DRY_RUN_READ_ONLY"):
        if n not in src: fail(f"module missing token: {n}")

    # Both flags must be unset in live env.
    if os.environ.get("SERVER_PROFILES_RUNTIME_ENABLED", "").lower() == "true":
        fail("SERVER_PROFILES_RUNTIME_ENABLED must remain unset/false in live env")
    if os.environ.get("SERVER_PROFILES_PREVIEW_ENABLED", "").lower() == "true":
        fail("SERVER_PROFILES_PREVIEW_ENABLED must remain unset/false in live env")

    # HTTP live: default 503 preserved (default route MUST be unchanged).
    code, body = _http("GET", "/api/server-profiles/select")
    if code != 503 or "disabled" not in body:
        fail(f"GET sp/select expected 503+disabled, got {code} body={body[:200]}")
    code, body = _http("POST", "/api/server-profiles/select")
    if code != 503 or "disabled" not in body:
        fail(f"POST sp/select expected 503+disabled, got {code} body={body[:200]}")
    code, body = _http("GET", "/api/heroes")
    if code != 200 or len(json.loads(body)) != 100:
        fail("heroes=100 invariant violated")

    # Unit-style: import helper and verify contract.
    sys.path.insert(0, "/app/backend")
    os.environ.pop("SERVER_PROFILES_RUNTIME_ENABLED", None)
    os.environ.pop("SERVER_PROFILES_PREVIEW_ENABLED", None)
    from routes.server_profiles import _preview_runtime_enabled, _preview_dry_run_envelope  # type: ignore
    if _preview_runtime_enabled() is not False:
        fail("_preview_runtime_enabled must be False with both flags unset")
    env = _preview_dry_run_envelope(None)
    for k in ("preview", "dry_run"):
        if env.get(k) is not True: fail(f"envelope {k} must be True")
    for k in ("mutation_executed", "active_server_switched", "dual_write_executed", "second_server_opened"):
        if env.get(k) is not False: fail(f"envelope {k} must be False")

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

    print("[PASS] PROJECT_D Track A flagged preview behavior OK: helpers present; double-flag unset; default 503; preview envelope inert; DB unchanged")
    sys.exit(0)

if __name__ == "__main__": main()
