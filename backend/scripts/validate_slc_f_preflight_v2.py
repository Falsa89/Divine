#!/usr/bin/env python3
"""SLC-F-PREFLIGHT v2 (PROJECT_E Track A) — reads _slc_c_combo_v2_result.json."""
import json, sys
from pathlib import Path

UPSTREAM = Path("/app/data/design/server_lifecycle/_slc_c_combo_v2_result.json")


def fail(m): print(f"[slc_f_preflight_v2] FAIL {m}"); sys.exit(1)


def main():
    if not UPSTREAM.exists(): fail(f"upstream missing: {UPSTREAM}")
    d = json.loads(UPSTREAM.read_text())
    if d.get("status") != "PASS":
        fail(f"SLC-C combo v2 status != PASS: {d.get('status')}")
    print("[slc_f_preflight_v2] PASS upstream SLC-C combo v2 OK")
    sys.exit(0)

if __name__ == "__main__": main()
