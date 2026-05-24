#!/usr/bin/env python3
"""PROJECT_E Track C validator: status effect non-runtime unit tests."""
import importlib.util, json, sys
from pathlib import Path

MARKER = Path("/app/data/design/status_effects/project_e_status_effect_non_runtime_ut_v1.json")
BASELINE = Path("/app/data/design/status_effects/project_c_status_effect_catalog_baseline_v1.json")
ADAPTER = Path("/app/backend/game_logic/status_effect_runtime_adapter_stub.py")
WATCH = (
    Path("/app/backend/server.py"),
    Path("/app/backend/game_logic/battle_engine.py"),
    Path("/app/backend/game_logic/battle_core.py"),
)
ROUTES = Path("/app/backend/routes")
NEEDLE = "status_effect_runtime_adapter_stub"


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_C_STATUS_EFFECT_NON_RUNTIME_UT_READY":
        fail("verdict mismatch")
    if m.get("unit_test_count") != 6: fail("unit_test_count must be 6")
    if not BASELINE.exists(): fail("upstream baseline missing")
    if not ADAPTER.exists(): fail("adapter stub missing")
    b = json.loads(BASELINE.read_text())
    effects = b.get("effects_baseline", [])
    cats = {c["id"] for c in b.get("canonical_categories", [])}

    spec = importlib.util.spec_from_file_location("_proj_e_status", ADAPTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # UT_STATUS_1: every catalog effect -> canonical category
    for e in effects:
        if e["category"] not in cats:
            fail(f"UT_STATUS_1 effect {e['id']} category {e['category']} not canonical")
        if e["category"] not in mod.CANONICAL_CATEGORIES:
            fail(f"UT_STATUS_1 effect {e['id']} category not in adapter CANONICAL_CATEGORIES")

    # UT_STATUS_2: stacking rules parse — each effect has duration_turns, stack_max in valid bounds
    for e in effects:
        if not (1 <= e["duration_turns"] <= 10):
            fail(f"UT_STATUS_2 effect {e['id']} duration_turns out of bounds")
        if not (1 <= e["stack_max"] <= 5):
            fail(f"UT_STATUS_2 effect {e['id']} stack_max out of bounds")

    # UT_STATUS_3: hard control (stun/freeze) must exist as control category effects
    control_effects = [e for e in effects if e["category"] == "control"]
    control_ids = {e["id"] for e in control_effects}
    for required in ("stun", "freeze"):
        if required not in control_ids:
            fail(f"UT_STATUS_3 hard control effect {required} missing from catalog")

    # UT_STATUS_4: dispellable/cleansable bool
    for e in effects:
        if not isinstance(e.get("dispellable"), bool):
            fail(f"UT_STATUS_4 effect {e['id']} dispellable not bool")
        if not isinstance(e.get("cleansable"), bool):
            fail(f"UT_STATUS_4 effect {e['id']} cleansable not bool")

    # UT_STATUS_5: no Borea-only status leak — no effect id contains 'borea'
    for e in effects:
        if "borea" in e["id"].lower():
            fail(f"UT_STATUS_5 catalog leaks Borea-only effect: {e['id']}")

    # UT_STATUS_6: adapter not imported by battle/runtime
    for f in WATCH:
        if f.exists() and NEEDLE in f.read_text():
            fail(f"UT_STATUS_6 adapter imported in: {f}")
    for f in ROUTES.glob("*.py"):
        if NEEDLE in f.read_text():
            fail(f"UT_STATUS_6 adapter imported in routes: {f}")

    print("[PASS] PROJECT_E Track C status effect non-runtime UT OK: 6/6 UT pass; adapter NOT imported by battle/runtime")
    sys.exit(0)

if __name__ == "__main__": main()
