#!/usr/bin/env python3
"""
V6 BLOCK_B validator (read-only).

Verifies the export script exists and the snapshot file (if present) is JSONL-parseable.
Does NOT execute the export. Safe in suite.

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

EXPORT_SCRIPT = Path("/app/backend/scripts/export_af2n_metrics_snapshot_v1.py")
SNAPSHOT = Path("/app/data/design/system_safety/af2n_metrics_snapshot.jsonl")
MARKER = Path("/app/data/design/system_safety/af2n_metrics_snapshot_export_v1.json")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not EXPORT_SCRIPT.exists():
        fail(f"missing export script: {EXPORT_SCRIPT}")
    if not MARKER.exists():
        fail(f"missing marker: {MARKER}")

    m = json.loads(MARKER.read_text(encoding="utf-8"))
    if m.get("verdict") != "BLOCK_B_AF2N_METRICS_SNAPSHOT_EXPORT_READY":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("runtime_patch_applied") is not False:
        fail("runtime_patch_applied must be false")

    # If the snapshot exists, verify JSONL parseability.
    if SNAPSHOT.exists():
        bad = 0
        for i, line in enumerate(SNAPSHOT.read_text(encoding="utf-8", errors="ignore").splitlines()):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except Exception:
                bad += 1
                if bad <= 3:
                    print(f"[WARN] malformed snapshot line {i+1}", file=sys.stderr)
        if bad:
            fail(f"{bad} malformed JSONL lines")

    print("[PASS] V6 BLOCK_B export script + marker integrity OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
