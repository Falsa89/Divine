#!/usr/bin/env python3
"""
V6 BLOCK_E validator suite runtime health (non-blocking).

Read-only HTTP smoke + supervisorctl status check + file mtime check.
WARNS on transient issues but does not FAIL the suite unless H1/H2 break.

Exit 0 PASS / 1 FAIL (only on H1/H2 hard failures).
"""
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "http://localhost:8001"
ROOT = Path("/app")
OBS_ROLLUP = ROOT / "data/design/server_lifecycle/_slc_f_observability_rollup_v1_result.json"

warnings: list[str] = []
errors: list[str] = []


def _http_get(path: str, timeout: float = 3.0) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(BASE_URL + path, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as exc:
        return -1, str(exc)


def h1_backend_responding() -> None:
    code, _ = _http_get("/api/heroes")
    if code != 200:
        errors.append(f"H1 backend not responding: HTTP {code}")


def h2_heroes_count_100() -> None:
    code, body = _http_get("/api/heroes")
    if code != 200:
        return  # already captured in H1
    try:
        data = json.loads(body)
    except Exception as exc:
        errors.append(f"H2 heroes JSON malformed: {exc}")
        return
    if not isinstance(data, list) or len(data) != 100:
        errors.append(f"H2 heroes count expected 100, got {len(data) if isinstance(data, list) else 'n/a'}")


def h3_redis_running() -> None:
    try:
        out = subprocess.run(
            ["sudo", "supervisorctl", "status", "redis"],
            capture_output=True, text=True, timeout=5,
        )
        if "RUNNING" not in out.stdout:
            warnings.append(
                f"H3 redis not RUNNING (status: {out.stdout.strip()}) \u2014 hint: bash /app/ops/ensure_redis_rate_limit.sh"
            )
    except Exception as exc:
        warnings.append(f"H3 redis status check skipped: {exc}")


def h4_mongodb_reachable() -> None:
    # Best-effort: try connecting via a TCP probe to localhost:27017.
    import socket
    try:
        with socket.create_connection(("localhost", 27017), timeout=2.0):
            pass
    except Exception as exc:
        warnings.append(f"H4 mongodb tcp probe failed: {exc}")


def h5_observability_rollup_fresh() -> None:
    if not OBS_ROLLUP.exists():
        warnings.append(f"H5 observability rollup missing: {OBS_ROLLUP}")
        return
    age = time.time() - OBS_ROLLUP.stat().st_mtime
    if age > 7 * 24 * 3600:
        warnings.append(f"H5 observability rollup stale (age={age:.0f}s)")


def main() -> None:
    h1_backend_responding()
    h2_heroes_count_100()
    h3_redis_running()
    h4_mongodb_reachable()
    h5_observability_rollup_fresh()

    for w in warnings:
        print(f"[WARN] {w}")
    if errors:
        print("[FAIL] V6 BLOCK_E suite runtime health:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print(f"[PASS] V6 BLOCK_E suite runtime health: H1/H2 OK; warnings={len(warnings)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
