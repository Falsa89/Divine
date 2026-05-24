#!/usr/bin/env python3
"""PROJECT_E Track E validator: QA login dry-run safety + no secret logging."""
import json, os, subprocess, sys
from pathlib import Path

MARKER = Path("/app/data/design/project_management/project_e_qa_test_creds_login_dryrun_v1.json")
WRAPPER = Path("/app/backend/scripts/run_project_d_qa_mobile_smoke_runner.py")
ENV_EXAMPLE = Path("/app/.env.qa_runner.example")

FORBIDDEN_LOG_PATTERNS = (
    "print(args.password",
    'print("password',
    "print(os.environ['QA_RUNNER_TEST_PASSWORD'])",
    "print(payload)",  # payload may contain creds; should never be raw-printed
)


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_E_QA_TEST_CREDS_LOGIN_MANUAL_REQUIRED":
        fail(f"verdict mismatch: {m.get('verdict')}")
    contract = m.get("login_dryrun_safety_contract", {})
    for k in ("no_signup_creation", "no_password_reset", "no_profile_mutation", "no_secret_print_to_stdout_or_stderr", "jwt_in_memory_only_no_disk_persistence", "json_report_excludes_credentials"):
        if contract.get(k) is not True: fail(f"contract.{k} must be True")
    forb = m.get("forbidden_in_track_e_respected", {})
    for k in ("account_creation", "real_gacha_spend", "paid_currency_mutation", "destructive_action", "secret_logging", "frontend"):
        if forb.get(k) is not False: fail(f"forbidden_in_track_e.{k} must be False")

    # Env example must exist as documentation (without real secret)
    if not ENV_EXAMPLE.exists(): fail(f"env example missing: {ENV_EXAMPLE}")
    env_src = ENV_EXAMPLE.read_text()
    if "__REPLACE_WITH_SAFE_STAGING_PASSWORD__" not in env_src:
        fail("env example must contain placeholder password (no real secret)")

    # Wrapper must NOT print raw creds
    if not WRAPPER.exists(): fail("wrapper missing")
    wsrc = WRAPPER.read_text()
    for p in FORBIDDEN_LOG_PATTERNS:
        if p in wsrc:
            fail(f"wrapper contains forbidden log pattern: {p}")

    # Live env: QA_RUNNER_LOGIN_ENABLED must be unset/false
    if os.environ.get("QA_RUNNER_LOGIN_ENABLED", "").lower() == "true":
        fail("QA_RUNNER_LOGIN_ENABLED must remain unset/false in live env")

    # Wrapper --help smoke
    try:
        r = subprocess.run([sys.executable, str(WRAPPER), "--help"], capture_output=True, timeout=5)
        if r.returncode != 0: fail(f"wrapper --help exit={r.returncode}")
    except subprocess.TimeoutExpired:
        fail("wrapper --help timeout")

    print("[PASS] PROJECT_E Track E QA login dry-run safety OK: live=MANUAL_REQUIRED; env example present; no secret patterns in wrapper")
    sys.exit(0)

if __name__ == "__main__": main()
