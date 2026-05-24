#!/usr/bin/env python3
"""PROJECT_D Track B validator: unit-test caps + contract on housing_bonus_resolver_stub.

NON importa il resolver a runtime live (legge solo il file source via importlib).
Verifica 8 casi UT_HOUSING_1..8 contro il contratto reale dello stub:

    resolve_housing_bonus(user_state: dict) -> dict
        - input dict (TypeError altrimenti)
        - output keys: hp_bonus, atk_bonus, def_bonus, healing_bonus (tutti 0)

    validate_caps_definition(caps: dict) -> List[str]
        - ritorna lista vuota se caps validi

    CANONICAL_CAPS dict con chiavi per_room/category/item/bonus/mode/master_cap

E che il modulo NON sia importato da server.py o routes/*.py.
"""
import importlib.util
import json
import sys
from pathlib import Path

MARKER = Path("/app/data/design/housing/project_d_housing_resolver_phase2_tests_v1.json")
STUB = Path("/app/backend/game_logic/housing_bonus_resolver_stub.py")
WATCH = [Path("/app/backend/server.py"), Path("/app/backend/game_systems.py")]
ROUTES = Path("/app/backend/routes")
NEEDLE = "housing_bonus_resolver_stub"


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_B_HOUSING_RESOLVER_PHASE2_TESTS_READY":
        fail("verdict mismatch")
    cases = m.get("unit_test_cases", [])
    if len(cases) != 8: fail(f"expected 8 unit_test_cases, got {len(cases)}")
    forb = m.get("forbidden_in_track_b_respected", {})
    for k in ("live_housing_runtime", "battle_account_stat_application", "db_writes", "frontend_ui", "runtime_import_of_stub"):
        if forb.get(k) is not False: fail(f"forbidden_in_track_b.{k} must be False")

    if not STUB.exists(): fail("stub missing")
    spec = importlib.util.spec_from_file_location("_proj_d_housing_stub", STUB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # UT_HOUSING_1: minimal dict input returns zero envelope with 4 canonical keys.
    env = mod.resolve_housing_bonus({"user_id": "u_test"})
    expected_keys = {"hp_bonus", "atk_bonus", "def_bonus", "healing_bonus"}
    if set(env.keys()) != expected_keys:
        fail(f"UT_HOUSING_1 envelope keys mismatch: {sorted(env.keys())}")
    for k in expected_keys:
        if env[k] != 0: fail(f"UT_HOUSING_1 {k} must be 0")

    # UT_HOUSING_2: non-dict input raises TypeError (defensive contract).
    try:
        mod.resolve_housing_bonus(None)
        fail("UT_HOUSING_2 must raise TypeError on None input")
    except TypeError:
        pass
    try:
        mod.resolve_housing_bonus([])
        fail("UT_HOUSING_2 must raise TypeError on list input")
    except TypeError:
        pass

    # UT_HOUSING_3: stable across multiple dict-shaped calls (zero envelope every time).
    env_v1 = mod.resolve_housing_bonus({"user_id": "u1", "housing_rooms": []})
    env_v2 = mod.resolve_housing_bonus({"user_id": "u2", "objects": [], "residents": []})
    if env_v1 != env or env_v2 != env:
        fail("UT_HOUSING_3 envelope must be stable across calls")

    # UT_HOUSING_4: validate_caps_definition(CANONICAL_CAPS) returns empty list (no errors).
    caps = getattr(mod, "CANONICAL_CAPS", None)
    if caps is None: fail("UT_HOUSING_4 CANONICAL_CAPS not exported")
    errors = mod.validate_caps_definition(caps)
    if errors != []: fail(f"UT_HOUSING_4 validate_caps_definition must return [], got {errors}")

    # UT_HOUSING_5: caps canonical key set covers per_room/category/item/bonus/mode/master_cap.
    expected_cap_keys = {"per_room", "category", "item", "bonus", "mode", "master_cap"}
    if set(caps.keys()) != expected_cap_keys:
        fail(f"UT_HOUSING_5 caps keys mismatch: {sorted(caps.keys())}")

    # UT_HOUSING_6: every cap value is a positive int.
    for k, v in caps.items():
        if not isinstance(v, int) or v <= 0:
            fail(f"UT_HOUSING_6 cap {k}={v} must be positive int")

    # UT_HOUSING_7: INERT_MARKER + INERT_BONUS_OUTPUT presence (frozen canonical).
    if not getattr(mod, "INERT_MARKER", "").startswith("HOUSING_BONUS_RESOLVER_STUB_INERT"):
        fail("UT_HOUSING_7 INERT_MARKER missing/invalid")
    inert = getattr(mod, "INERT_BONUS_OUTPUT", None)
    if not isinstance(inert, dict) or set(inert.keys()) != expected_keys:
        fail("UT_HOUSING_7 INERT_BONUS_OUTPUT shape invalid")
    if any(v != 0 for v in inert.values()):
        fail("UT_HOUSING_7 INERT_BONUS_OUTPUT must be all zero")

    # UT_HOUSING_8: no runtime import.
    for f in WATCH:
        if f.exists() and NEEDLE in f.read_text():
            fail(f"UT_HOUSING_8 runtime import detected: {f}")
    for f in ROUTES.glob("*.py"):
        if NEEDLE in f.read_text():
            fail(f"UT_HOUSING_8 runtime import in routes: {f}")

    print("[PASS] PROJECT_D Track B housing resolver phase2 unit tests OK: 8/8 UT pass; stub NOT imported by runtime")
    sys.exit(0)

if __name__ == "__main__": main()
