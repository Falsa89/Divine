#!/usr/bin/env python3
"""Rollback for PROJECT_D Track A flagged preview helper (gated).

Use: PROJECT_D_TRACK_A_ROLLBACK=YES python3 rollback_project_d_server_profiles_flagged_preview.py

The rollback strategy is documentary: removal of the preview helper from
`/app/backend/routes/server_profiles.py` must be done via `git checkout` or a
search-replace removing the PROJECT_D Track A block. This script verifies the
gate marker and prints the precise instructions.
"""
import os, sys

GATE = "PROJECT_D_TRACK_A_ROLLBACK"

def main():
    if os.environ.get(GATE, "").strip().upper() != "YES":
        print(f"[GATE] rollback aborted — set {GATE}=YES to proceed")
        sys.exit(2)
    print("[ROLLBACK] PROJECT_D Track A preview helper removal")
    print("  manual step: revert /app/backend/routes/server_profiles.py via git diff or remove the")
    print("  block delimited by `PROJECT_D TRACK A — FLAGGED PREVIEW BEHAVIOR` (PURE; no runtime call).")
    print("  No DB rollback required (zero writes performed during V_D).")
    sys.exit(0)

if __name__ == "__main__":
    main()
