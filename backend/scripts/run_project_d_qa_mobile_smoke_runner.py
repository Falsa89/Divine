#!/usr/bin/env python3
"""PROJECT_D Track E — QA Mobile Smoke Runner WRAPPER with gated LOGIN step.

Wrapper attorno a `/app/backend/scripts/qa_mobile_smoke_runner.py` (V_C Track E)
che aggiunge un **login step gated**:
  - Esegue POST /api/login SOLO se:
      QA_RUNNER_LOGIN_ENABLED=true
      QA_RUNNER_TEST_EMAIL e QA_RUNNER_TEST_PASSWORD entrambi presenti
  - Altrimenti emette voce MANUAL_REQUIRED nel report e prosegue con
    il runner non-mutating V_C come fallback.

Il wrapper NON crea utenti, NON ripristina password, NON esegue POST
diverse da /api/login.

Usage:
    python3 run_project_d_qa_mobile_smoke_runner.py [--base http://localhost:8001] [--json-out PATH]

Exit 0 = tutto OK (login eseguito o MANUAL_REQUIRED) e step non-mutating tutti OK.
Exit 1 = step non-mutating fallito oppure login 4xx/5xx (se attivato).
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

BASE_DEFAULT = "http://localhost:8001"
UNDERLYING_RUNNER = Path("/app/backend/scripts/qa_mobile_smoke_runner.py")

LOGIN_FLAG = "QA_RUNNER_LOGIN_ENABLED"
EMAIL_ENV = "QA_RUNNER_TEST_EMAIL"
PASSWORD_ENV = "QA_RUNNER_TEST_PASSWORD"


def _login_enabled() -> bool:
    return os.environ.get(LOGIN_FLAG, "").strip().lower() == "true"


def _have_creds() -> bool:
    return bool(os.environ.get(EMAIL_ENV)) and bool(os.environ.get(PASSWORD_ENV))


def _login_step(base: str) -> dict:
    """Esegue POST /api/login solo se flag + creds. Altrimenti MANUAL_REQUIRED."""
    started = time.time()
    if not _login_enabled():
        return {"step": 1, "name": "LOGIN", "status": "MANUAL_REQUIRED", "reason": f"{LOGIN_FLAG} not enabled", "duration_s": 0.0}
    if not _have_creds():
        return {"step": 1, "name": "LOGIN", "status": "MANUAL_REQUIRED", "reason": f"{EMAIL_ENV}/{PASSWORD_ENV} missing", "duration_s": 0.0}
    payload = json.dumps({"email": os.environ[EMAIL_ENV], "password": os.environ[PASSWORD_ENV]}).encode("utf-8")
    req = urllib.request.Request(base + "/api/login", data=payload, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return {"step": 1, "name": "LOGIN", "status": "OK", "http": resp.status,
                    "duration_s": round(time.time() - started, 3),
                    "jwt_stored_in_memory_only": True}
    except urllib.error.HTTPError as e:
        return {"step": 1, "name": "LOGIN", "status": "FAIL", "http": e.code,
                "duration_s": round(time.time() - started, 3), "ok": False}
    except Exception as exc:
        return {"step": 1, "name": "LOGIN", "status": "FAIL", "http": -1,
                "reason": str(exc), "duration_s": round(time.time() - started, 3), "ok": False}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="run_project_d_qa_mobile_smoke_runner")
    ap.add_argument("--base", default=BASE_DEFAULT)
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args(argv)

    if not UNDERLYING_RUNNER.exists():
        print("[FAIL] underlying runner missing")
        return 1

    login = _login_step(args.base)

    # Esegue runner V_C; cattura output JSON.
    tmp_out = "/tmp/_qa_v_c_inner_report.json"
    proc = subprocess.run([sys.executable, str(UNDERLYING_RUNNER), "--base", args.base, "--json-out", tmp_out],
                          capture_output=True, timeout=60)
    inner = {}
    if Path(tmp_out).exists():
        try: inner = json.loads(Path(tmp_out).read_text())
        except Exception: inner = {"parse_error": True}

    report = {
        "task_id": "PROJECT_D_TRACK_E_QA_RUNNER_LOGIN_GATED_EXECUTION",
        "login_step": login,
        "inner_runner": inner,
        "all_inner_ok": inner.get("all_executed_ok", False),
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
    }
    if args.json_out:
        try: Path(args.json_out).write_text(json.dumps(report, indent=2))
        except Exception as exc: print(f"[WARN] {exc}")
    print(json.dumps(report, indent=2))
    # Exit logic: login FAIL → 1; inner not ok → 1
    if login.get("status") == "FAIL": return 1
    if not report["all_inner_ok"]: return 1
    return 0

if __name__ == "__main__": sys.exit(main())
