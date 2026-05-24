#!/usr/bin/env python3
"""PROJECT_C Track E validator (read-only).

Verifica:
- marker JSON presente con verdict atteso
- runner CLI presente in /app/backend/scripts/qa_mobile_smoke_runner.py
- runner non importa funzioni mutating dal backend (no requests POST hardcoded)
- runner espone --help senza errori (smoke test del CLI)

NON esegue il runner contro il backend nella suite (eviterebbe accoppiamenti).

Exit 0 PASS / 1 FAIL.
"""
import json
import subprocess
import sys
from pathlib import Path

MARKER = Path("/app/data/design/project_management/project_c_qa_mobile_smoke_runner_v1.json")
RUNNER = Path("/app/backend/scripts/qa_mobile_smoke_runner.py")
UPSTREAM = Path("/app/data/design/project_management/project_b_qa_release_mobile_smoke_flow_v1.json")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not MARKER.exists():
        fail(f"missing marker {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_E_QA_MOBILE_SMOKE_RUNNER_IMPLEMENTED_NON_MUTATING":
        fail(f"verdict mismatch: {m.get('verdict')}")
    if m.get("db_writes_executed") != 0:
        fail("db_writes_executed must be 0")
    if m.get("runtime_patch_applied") is not False:
        fail("runtime_patch_applied must be False")
    caps = m.get("runner_capabilities", {})
    if caps.get("executes_only_GET_endpoints") is not True:
        fail("runner must execute only GET")
    if caps.get("skips_mutating_step_9_by_default") is not True:
        fail("runner must skip step 9 by default")
    if caps.get("performs_real_summon") is not False:
        fail("runner must NOT perform real summon")
    if caps.get("performs_real_battle") is not False:
        fail("runner must NOT perform real battle")
    forb = m.get("forbidden_in_track_e_respected", {})
    for k in ("db_mutation", "battle_execution", "summon_real_spend", "af2n_runtime_flip", "pipeline_hook_to_supervisord", "ci_integration"):
        if forb.get(k) is not False:
            fail(f"forbidden_in_track_e.{k} must be False")
    if not RUNNER.exists():
        fail(f"runner missing: {RUNNER}")
    src = RUNNER.read_text()
    # Nessuna chiamata POST a endpoint live consentita dal runner.
    forbidden_tokens = (".post(", 'method="POST"', "method='POST'", "requests.post", "requests.delete", "requests.put", "requests.patch")
    for tok in forbidden_tokens:
        if tok in src:
            fail(f"runner contains forbidden mutating token: {tok}")
    if "DEFAULT_EXECUTED_STEPS" not in src or "DEFAULT_SKIPPED_STEPS" not in src:
        fail("runner missing default step sets")
    if not UPSTREAM.exists():
        fail("upstream V_B matrix missing")
    # Smoke CLI --help (no backend call)
    try:
        r = subprocess.run([sys.executable, str(RUNNER), "--help"], capture_output=True, timeout=5)
        if r.returncode != 0:
            fail(f"runner --help exit={r.returncode}: {r.stderr.decode('utf-8','ignore')[:200]}")
        out = r.stdout.decode("utf-8", "ignore")
        if "--include-mutating" not in out or "--json-out" not in out:
            fail("runner --help missing expected flags")
    except subprocess.TimeoutExpired:
        fail("runner --help timeout")
    print("[PASS] PROJECT_C Track E QA mobile smoke runner OK: GET-only, step 9 skipped, no POST/mutation tokens, --help OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
