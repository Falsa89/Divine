#!/usr/bin/env python3
"""PROJECT_C Track B validator (read-only)."""
import json, sys
from pathlib import Path

DESIGN = Path("/app/data/design/housing/project_c_housing_resolver_integration_design_v1.json")
STUB = Path("/app/backend/game_logic/housing_bonus_resolver_stub.py")
WATCH = [Path("/app/backend/server.py"), Path("/app/backend/game_systems.py")]
ROUTES = Path("/app/backend/routes")


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def main():
    if not DESIGN.exists(): fail(f"missing {DESIGN}")
    m = json.loads(DESIGN.read_text())
    if m.get("verdict") != "TRACK_B_HOUSING_RESOLVER_INTEGRATION_DESIGN_READY":
        fail("verdict mismatch")
    if m.get("resolver_imported_by_runtime") is not False:
        fail("resolver_imported_by_runtime must be False")
    phases = m.get("integration_phases", [])
    if len(phases) < 5: fail(f"expected 5 phases, got {len(phases)}")
    if phases[4].get("status") != "FORBIDDEN_OUT_OF_SCOPE_PROJECT_C":
        fail("phase 5 must be FORBIDDEN_OUT_OF_SCOPE_PROJECT_C")

    if not STUB.exists(): fail("stub missing (V_B Track B regression)")
    needle = "housing_bonus_resolver_stub"
    for f in WATCH:
        if f.exists() and needle in f.read_text():
            fail(f"runtime import detected: {f}")
    for f in ROUTES.glob("*.py"):
        if needle in f.read_text():
            fail(f"runtime import in routes: {f}")
    print("[PASS] PROJECT_C Track B housing resolver integration design OK; 5 phases; stub still NOT imported by runtime")
    sys.exit(0)

if __name__ == "__main__": main()
