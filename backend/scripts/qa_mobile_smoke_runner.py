#!/usr/bin/env python3
"""
PROJECT_C Track E — QA Mobile Smoke Runner CLI (non-mutating).

Legge la matrice da `/app/data/design/project_management/project_b_qa_release_mobile_smoke_flow_v1.json`
ed esegue **solo gli step non-mutating GET-only**. Lo step mutating 9
(`SLC_GUARD_LEGACY_SERVER_SELECT`) è skippato di default. Lo step 1 LOGIN è
skippato (no credenziali). Step gacha/battle/auth sono fuori scope di V_C.

Usage:
    python3 qa_mobile_smoke_runner.py [--base http://localhost:8001] [--json-out PATH] [--include-mutating]

Exit 0 = tutti gli step eseguiti hanno match con expected.
Exit 1 = almeno uno step ha discrepanza.

NON modifica DB. NON triggera summon. NON triggera battle.
"""
import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

MATRIX_PATH = Path("/app/data/design/project_management/project_b_qa_release_mobile_smoke_flow_v1.json")
DEFAULT_BASE = "http://localhost:8001"
DEFAULT_TIMEOUT = 8

# Step di V_B che il runner V_C esegue di default (tutti non-mutating GET-only).
DEFAULT_EXECUTED_STEPS = {2, 3, 4, 10, 12}
# Step skippati per design in V_C (auth/mutating/fuori scope).
DEFAULT_SKIPPED_STEPS = {1, 5, 6, 7, 9, 11, 13}


def _http_get(base: str, path: str, timeout: int = DEFAULT_TIMEOUT) -> tuple[int, str]:
    try:
        req = urllib.request.Request(base + path, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "ignore")
        except Exception:
            body = ""
        return e.code, body
    except Exception as exc:
        return -1, f"<ERR: {exc}>"


def _step_run(base: str, step: dict) -> dict:
    """Esegue uno step della matrice. Solo step canonici hanno verifica esplicita."""
    name = step.get("name")
    started = time.time()
    if name == "HEROES_CATALOG":
        code, body = _http_get(base, "/api/heroes")
        ok = code == 200
        try:
            count = len(json.loads(body)) if ok else None
        except Exception:
            count = None
        ok = ok and count == 100
        return {"step": step.get("step"), "name": name, "http": code, "len": count, "ok": ok, "duration_s": round(time.time() - started, 3)}
    if name == "BOREA_INERT":
        code, _ = _http_get(base, "/api/heroes/borea")
        return {"step": step.get("step"), "name": name, "http": code, "ok": code == 200, "duration_s": round(time.time() - started, 3)}
    if name == "PRIMORDIAL_GAIA_INERT":
        code, _ = _http_get(base, "/api/heroes/primordial_gaia")
        return {"step": step.get("step"), "name": name, "http": code, "ok": code == 404, "duration_s": round(time.time() - started, 3)}
    if name == "SLC_GUARD_NEW_DUAL_ROUTE":
        code, body = _http_get(base, "/api/server-profiles/select")
        ok = code == 503 and "disabled" in body.lower()
        return {"step": step.get("step"), "name": name, "http": code, "ok": ok, "duration_s": round(time.time() - started, 3)}
    if name == "HOUSING_PLACEHOLDER":
        code, _ = _http_get(base, "/api/housing/rooms")
        return {"step": step.get("step"), "name": name, "http": code, "ok": code == 404, "duration_s": round(time.time() - started, 3)}
    # Step non riconosciuto dal runner V_C → registrato come SKIPPED_UNKNOWN.
    return {"step": step.get("step"), "name": name, "http": None, "ok": False, "reason": "UNKNOWN_STEP_IN_RUNNER_V_C", "duration_s": 0.0}


def run(base: str, include_mutating: bool, json_out: str | None) -> int:
    if not MATRIX_PATH.exists():
        print(f"[FAIL] matrix missing: {MATRIX_PATH}")
        return 1
    matrix = json.loads(MATRIX_PATH.read_text()).get("smoke_flow_matrix", [])
    if not matrix:
        print("[FAIL] empty matrix")
        return 1

    executed_set = set(DEFAULT_EXECUTED_STEPS)
    # In V_C il flag include-mutating resta sempre OFF; lasciato per estensibilità.
    if include_mutating:
        # In future packs si aggiungerà step 9 gated; per ora si lascia inerte.
        pass

    results = []
    skipped = []
    all_ok = True
    for step in matrix:
        sid = step.get("step")
        if sid in executed_set:
            r = _step_run(base, step)
            results.append(r)
            if not r.get("ok"):
                all_ok = False
        else:
            skipped.append({"step": sid, "name": step.get("name"), "reason": "non_mutating_runner_v_c_skip"})

    report = {
        "task_id": "PROJECT_C_TRACK_E_QA_MOBILE_SMOKE_RUNNER_EXECUTION",
        "base": base,
        "include_mutating": include_mutating,
        "matrix_total_steps": len(matrix),
        "executed_count": len(results),
        "skipped_count": len(skipped),
        "all_executed_ok": all_ok,
        "executed": results,
        "skipped": skipped,
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
    }
    if json_out:
        try:
            Path(json_out).write_text(json.dumps(report, indent=2))
        except Exception as exc:
            print(f"[WARN] could not write report: {exc}")
    print(json.dumps(report, indent=2))
    return 0 if all_ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="qa_mobile_smoke_runner")
    ap.add_argument("--base", default=DEFAULT_BASE, help="Backend base URL (default http://localhost:8001)")
    ap.add_argument("--json-out", default=None, help="Path JSON report output")
    ap.add_argument("--include-mutating", action="store_true",
                    help="Future flag; in V_C resta inerte e non abilita step 9")
    args = ap.parse_args(argv)
    return run(args.base, args.include_mutating, args.json_out)


if __name__ == "__main__":
    sys.exit(main())
