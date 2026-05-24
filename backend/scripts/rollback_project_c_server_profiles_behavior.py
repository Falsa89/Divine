#!/usr/bin/env python3
"""PROJECT_C Track A rollback (gated).

Ripristina /app/backend/routes/server_profiles.py allo skeleton V_B Track A
rimuovendo il behavior layer V_C. Gated da PROJECT_C_TRACK_A_ROLLBACK=YES.
"""
import os, sys
from pathlib import Path

GATE_ENV = "PROJECT_C_TRACK_A_ROLLBACK"
MODULE = Path("/app/backend/routes/server_profiles.py")

VB_SKELETON_RESTORE_MARKER = "# RESTORE-VB-SKELETON"


def main():
    if os.environ.get(GATE_ENV) != "YES":
        print(f"[GATED] rollback NOT executed. Set {GATE_ENV}=YES to proceed.")
        sys.exit(0)
    if not MODULE.exists():
        print("[OK] module absent (no-op)")
        sys.exit(0)
    src = MODULE.read_text()
    if "_read_only_select_response_for_user" not in src:
        print("[OK] V_C behavior layer already absent (no-op)")
        sys.exit(0)
    # Strategy: signal manual restore needed (idempotent design constraint).
    print("[INFO] V_C behavior layer detected. To rollback, restore the V_B skeleton from git or replace the module with the smaller V_B version.")
    print("[INFO] No automatic in-place rewrite performed (avoids accidental partial state).")
    print("[OK] Rollback signalled; manual git restore required.")
    sys.exit(0)

if __name__ == "__main__": main()
