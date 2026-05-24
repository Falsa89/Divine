#!/usr/bin/env python3
"""
PROJECT_B Track A validator (read-only + HTTP smoke).

Verifica:
- result JSON integro
- modulo routes/server_profiles.py esiste e contiene la gating logic attesa
- inclusione nel server.py presente
- feature flag SERVER_PROFILES_RUNTIME_ENABLED unset (no runtime activation)
- HTTP smoke: GET/POST /api/server-profiles/select restituiscono 503 con payload disabled
- /api/heroes invariato (100)

Exit 0 PASS / 1 FAIL.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

RESULT = Path("/app/data/design/server_lifecycle/project_b_server_profiles_dual_route_result_v1.json")
MODULE = Path("/app/backend/routes/server_profiles.py")
SERVER_PY = Path("/app/backend/server.py")
BASE_URL = "http://localhost:8001"


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def _http(method: str, path: str, timeout: float = 5.0):
    req = urllib.request.Request(BASE_URL + path, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="ignore")
        except Exception:
            body = ""
        return e.code, body
    except Exception as exc:
        return -1, str(exc)


def main() -> None:
    if not RESULT.exists():
        fail(f"missing result: {RESULT}")
    m = json.loads(RESULT.read_text(encoding="utf-8"))
    if m.get("verdict") != "TRACK_A_SERVER_PROFILES_DUAL_ROUTE_SKELETON_APPLIED_SAFE":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("feature_flag") != "SERVER_PROFILES_RUNTIME_ENABLED":
        fail("feature_flag canonical name mismatch")
    if m.get("db_writes_executed") != 0:
        fail("db_writes_executed must be 0")

    if not MODULE.exists():
        fail(f"missing routes module: {MODULE}")
    src = MODULE.read_text(encoding="utf-8")
    for needle in ('SERVER_PROFILES_RUNTIME_ENABLED', '"/api/server-profiles"', 'status_code=503',
                   'PROJECT_B_TRACK_A_INERT_SKELETON'):
        if needle not in src:
            fail(f"routes module missing expected token: {needle}")

    if not SERVER_PY.exists():
        fail(f"missing server.py: {SERVER_PY}")
    server_src = SERVER_PY.read_text(encoding="utf-8")
    if 'from routes.server_profiles import router as server_profiles_router' not in server_src:
        fail("server.py does not import server_profiles router")
    if 'app.include_router(server_profiles_router)' not in server_src:
        fail("server.py does not include server_profiles router")

    # Feature flag must remain unset.
    if os.environ.get("SERVER_PROFILES_RUNTIME_ENABLED"):
        fail("SERVER_PROFILES_RUNTIME_ENABLED must remain unset in current env")

    # HTTP smoke.
    code, body = _http("GET", "/api/server-profiles/select")
    if code != 503:
        fail(f"GET /api/server-profiles/select expected 503, got {code}")
    if 'disabled' not in body:
        fail("GET response payload missing 'disabled' token")

    code, body = _http("POST", "/api/server-profiles/select")
    if code != 503:
        fail(f"POST /api/server-profiles/select expected 503, got {code}")
    if 'disabled' not in body:
        fail("POST response payload missing 'disabled' token")

    # heroes invariant
    code, body = _http("GET", "/api/heroes")
    if code != 200:
        fail(f"GET /api/heroes expected 200, got {code}")
    try:
        n = len(json.loads(body))
    except Exception as exc:
        fail(f"heroes body JSON parse error: {exc}")
    if n != 100:
        fail(f"heroes count expected 100, got {n}")

    print("[PASS] PROJECT_B Track A dual-route skeleton OK (503 inert, flag unset, heroes=100, no DB write)")
    sys.exit(0)


if __name__ == "__main__":
    main()
