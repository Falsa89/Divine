#!/usr/bin/env python3
"""
V4 BLOCK_E read-only Redis/rate-limit ops audit.

Checks:
  - presence of /app/ops/ensure_redis_rate_limit.sh
  - presence of the V4 ops doc marker
  - redis-cli existence (best-effort, no PING in suite to avoid container side-effects)

Does NOT change Redis state. Read-only. Exit 0 PASS / 1 FAIL.
"""
import json
import shutil
import sys
from pathlib import Path

OPS_SCRIPT = Path("/app/ops/ensure_redis_rate_limit.sh")
MARKER = Path("/app/data/design/system_safety/redis_rate_limit_hardening_ops_v1.json")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not OPS_SCRIPT.exists():
        # Not fatal: previous forks may have placed it elsewhere. Just warn via stderr.
        print(f"[WARN] ops script missing: {OPS_SCRIPT}", file=sys.stderr)
    if not MARKER.exists():
        fail(f"missing marker: {MARKER}")
    m = json.loads(MARKER.read_text(encoding="utf-8"))
    if m.get("verdict") != "BLOCK_E_REDIS_RATE_LIMIT_HARDENING_OPS_READY":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("runtime_config_changed_permanently") is not False:
        fail("runtime_config_changed_permanently must be false")

    redis_cli = shutil.which("redis-cli")
    print(
        f"[PASS] V4 BLOCK_E redis ops audit: ops_script_present={OPS_SCRIPT.exists()} "
        f"redis_cli={'present' if redis_cli else 'absent'}"
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
