#!/usr/bin/env python3
"""PROJECT_D Track E validator (read-only + --help smoke).

Verifica:
- marker JSON con verdict atteso
- wrapper presente, no destructive POST (solo /api/login)
- assenza di endpoint POST proibiti hardcoded
- live state è MANUAL_REQUIRED se creds non disponibili
- --help OK
"""
import json, os, subprocess, sys
from pathlib import Path

MARKER = Path("/app/data/design/project_management/project_d_qa_runner_login_step_v1.json")
WRAPPER = Path("/app/backend/scripts/run_project_d_qa_mobile_smoke_runner.py")
UNDERLYING = Path("/app/backend/scripts/qa_mobile_smoke_runner.py")

FORBIDDEN_POST_PATTERNS = [
    "/api/server/select", "/api/server-profiles/select",
    "/api/gacha/pull", "/api/gacha/pull10",
    "/api/affinity/gift-spend", "/api/battle/",
    "/api/summon/pull",
]


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_E_QA_RUNNER_LOGIN_STEP_GATED_READY":
        fail(f"verdict mismatch: {m.get('verdict')}")
    if m.get("creates_users") is not False: fail("creates_users must be False")
    if m.get("mutates_account_state") is not False: fail("mutates_account_state must be False")
    if m.get("runtime_patch_applied") is not False: fail("runtime_patch_applied must be False")
    forb = m.get("forbidden_in_track_e_respected", {})
    for k in ("real_gacha_spend", "paid_currency_mutation", "destructive_action", "frontend", "user_creation", "account_state_mutation"):
        if forb.get(k) is not False: fail(f"forbidden_in_track_e.{k} must be False")

    if not WRAPPER.exists(): fail("wrapper missing")
    if not UNDERLYING.exists(): fail("underlying V_C runner missing")
    src = WRAPPER.read_text()
    for p in FORBIDDEN_POST_PATTERNS:
        if p in src: fail(f"wrapper contains forbidden POST pattern: {p}")
    # Allowed POST: only /api/login
    if "/api/login" not in src: fail("wrapper must reference /api/login")
    # Live env must lack QA_RUNNER creds (we are MANUAL_REQUIRED)
    if os.environ.get("QA_RUNNER_LOGIN_ENABLED", "").lower() == "true":
        fail("QA_RUNNER_LOGIN_ENABLED must remain unset/false in live env")
    # --help smoke
    try:
        r = subprocess.run([sys.executable, str(WRAPPER), "--help"], capture_output=True, timeout=5)
        if r.returncode != 0:
            fail(f"wrapper --help exit={r.returncode}")
        if "--json-out" not in r.stdout.decode("utf-8", "ignore"):
            fail("wrapper --help missing --json-out")
    except subprocess.TimeoutExpired:
        fail("wrapper --help timeout")
    print("[PASS] PROJECT_D Track E QA runner LOGIN step gated OK: wrapper present; only /api/login POST; live state MANUAL_REQUIRED")
    sys.exit(0)

if __name__ == "__main__": main()
