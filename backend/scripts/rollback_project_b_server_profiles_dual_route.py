#!/usr/bin/env python3
"""
PROJECT_B Track A rollback (gated).

Rimuove le 2 righe di include_router + import da server.py e cancella il modulo
routes/server_profiles.py. Gated da PROJECT_B_TRACK_A_ROLLBACK=YES.

Exit 0 OK / 1 FAIL.
"""
import os
import sys
from pathlib import Path

GATE_ENV = "PROJECT_B_TRACK_A_ROLLBACK"
GATE_OK = "YES"
MODULE = Path("/app/backend/routes/server_profiles.py")
SERVER_PY = Path("/app/backend/server.py")

IMPORT_BLOCK = (
    "\n# ===================== SERVER PROFILES DUAL-ROUTE SKELETON (PROJECT_B Track A) =====================\n"
    "# Inert flag-gated routes. Runtime OFF by default via SERVER_PROFILES_RUNTIME_ENABLED.\n"
    "# When the flag is unset, both GET and POST /api/server-profiles/select return HTTP 503\n"
    "# with a status=\"disabled\" payload. No DB writes, no behavior exposure.\n"
    "# Upstream design: 122D (V8 BLOCK_D dual-route), 123A (collection live inert).\n"
    "from routes.server_profiles import router as server_profiles_router\n"
    "app.include_router(server_profiles_router)"
)


def main() -> None:
    if os.environ.get(GATE_ENV) != GATE_OK:
        print(f"[GATED] rollback NOT executed. Set {GATE_ENV}={GATE_OK} to proceed.")
        sys.exit(0)

    if not SERVER_PY.exists():
        print(f"[FAIL] server.py missing: {SERVER_PY}")
        sys.exit(1)
    src = SERVER_PY.read_text(encoding="utf-8")
    if IMPORT_BLOCK in src:
        src = src.replace(IMPORT_BLOCK, "")
        SERVER_PY.write_text(src, encoding="utf-8")
        print("[OK] removed server_profiles router include from server.py")
    else:
        print("[OK] server.py already cleaned (no-op)")

    if MODULE.exists():
        MODULE.unlink()
        print(f"[OK] removed module {MODULE}")
    else:
        print(f"[OK] module already absent: {MODULE}")

    print("[OK] PROJECT_B Track A rollback complete. Restart backend with: sudo supervisorctl restart backend")
    sys.exit(0)


if __name__ == "__main__":
    main()
