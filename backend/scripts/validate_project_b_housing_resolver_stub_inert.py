#!/usr/bin/env python3
"""
PROJECT_B Track B validator (read-only).

Verifica:
- modulo housing_bonus_resolver_stub.py presente nel package game_logic
- INERT_MARKER presente
- resolve_housing_bonus restituisce 0 per ogni bonus chiave
- validate_caps_definition rileva caps invalide
- modulo NON importato da server.py / game_systems.py / battle_engine.py / battle_core.py / routes/* / frontend

Exit 0 PASS / 1 FAIL.
"""
import sys
from pathlib import Path

MODULE = Path("/app/backend/game_logic/housing_bonus_resolver_stub.py")
MARKER = Path("/app/data/design/housing/project_b_housing_mvp_resolver_stub_v1.json")

WATCHED_RUNTIME_FILES = [
    Path("/app/backend/server.py"),
    Path("/app/backend/game_systems.py"),
    Path("/app/backend/battle_engine.py"),
    Path("/app/backend/battle_core.py"),
]
ROUTES_DIR = Path("/app/backend/routes")
FRONTEND_APP_DIR = Path("/app/frontend/app")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not MARKER.exists():
        fail(f"missing marker: {MARKER}")
    if not MODULE.exists():
        fail(f"missing module: {MODULE}")

    # Import the module dynamically and exercise its public API.
    sys.path.insert(0, '/app/backend')
    try:
        from game_logic.housing_bonus_resolver_stub import (
            INERT_MARKER, CANONICAL_CAPS, INERT_BONUS_OUTPUT,
            resolve_housing_bonus, validate_caps_definition,
        )
    except Exception as exc:
        fail(f"import failed: {exc}")

    if INERT_MARKER != "HOUSING_BONUS_RESOLVER_STUB_INERT_PROJECT_B_TRACK_B_V1":
        fail(f"unexpected INERT_MARKER: {INERT_MARKER}")
    for key in ("per_room", "category", "item", "bonus", "mode", "master_cap"):
        if key not in CANONICAL_CAPS:
            fail(f"missing canonical cap key: {key}")
    out = resolve_housing_bonus({"user_id": "u1", "housing_rooms": [], "objects": [], "residents": []})
    for k in ("hp_bonus", "atk_bonus", "def_bonus", "healing_bonus"):
        if out.get(k) != 0:
            fail(f"resolve_housing_bonus must return 0 for {k}, got {out.get(k)}")
    # Caps validation negative case.
    errs = validate_caps_definition({"per_room": -1})
    if not errs:
        fail("validate_caps_definition must report errors for negative caps and missing keys")

    # Non-runtime import check.
    needle = "housing_bonus_resolver_stub"
    for f in WATCHED_RUNTIME_FILES:
        if f.exists() and needle in f.read_text(encoding="utf-8"):
            fail(f"runtime import detected: {f}")
    for f in ROUTES_DIR.glob("*.py"):
        if needle in f.read_text(encoding="utf-8"):
            fail(f"runtime import detected in routes: {f}")
    # Frontend non-import (search top-level app dir).
    if FRONTEND_APP_DIR.exists():
        for f in FRONTEND_APP_DIR.rglob("*.tsx"):
            try:
                if needle in f.read_text(encoding="utf-8"):
                    fail(f"frontend reference detected: {f}")
            except Exception:
                pass

    print("[PASS] PROJECT_B Track B HousingBonusResolver inert stub OK; returns 0; NOT imported by runtime")
    sys.exit(0)


if __name__ == "__main__":
    main()
