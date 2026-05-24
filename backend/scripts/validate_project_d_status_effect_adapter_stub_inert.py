#!/usr/bin/env python3
"""PROJECT_D Track C validator (read-only + contract test).

- marker JSON con verdict atteso
- modulo stub presente; importabile; contract `build_status_mapping` corretto
- stub NON importato da server.py, routes/*.py, game_logic/battle_*.py, frontend/app/combat.tsx (se esiste)

Exit 0 PASS / 1 FAIL.
"""
import importlib.util
import json
import sys
from pathlib import Path

MARKER = Path("/app/data/design/status_effects/project_d_status_effect_runtime_adapter_skeleton_v1.json")
STUB = Path("/app/backend/game_logic/status_effect_runtime_adapter_stub.py")
WATCH_FILES = [
    Path("/app/backend/server.py"),
    Path("/app/backend/game_logic/battle_engine.py"),
    Path("/app/backend/game_logic/battle_core.py"),
    Path("/app/frontend/app/combat.tsx"),
]
ROUTES = Path("/app/backend/routes")
NEEDLE = "status_effect_runtime_adapter_stub"


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_C_STATUS_EFFECT_RUNTIME_ADAPTER_SKELETON_CREATED_INERT":
        fail(f"verdict mismatch: {m.get('verdict')}")
    if m.get("runtime_patch_applied") is not False:
        fail("runtime_patch_applied must be False")
    if m.get("status_effects_runtime_active") is not False:
        fail("status_effects_runtime_active must be False")
    if m.get("adapter_imported_by_battle_or_combat") is not False:
        fail("adapter_imported_by_battle_or_combat must be False")
    forb = m.get("forbidden_in_track_c_respected", {})
    for k in ("battle_engine_changes", "battle_core_changes", "combat_tsx_changes",
              "status_live_activation", "hp_bar_status_ui_changes", "vfx_runtime", "borea_activation"):
        if forb.get(k) is not False: fail(f"forbidden_in_track_c.{k} must be False")

    if not STUB.exists(): fail("stub missing")
    spec = importlib.util.spec_from_file_location("_proj_d_status_stub", STUB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if mod.validate_canonical_sets() is not True:
        fail("validate_canonical_sets must return True")
    out = mod.build_status_mapping("atk_up_pct", "buff_offensive", "positive", "stack_capped", "normal", False, "buff_icon")
    expected_keys = {"status_id", "category", "polarity", "stacking", "boss_behavior", "source_lock", "display_hint", "contract_version", "runtime_active"}
    if set(out.keys()) != expected_keys:
        fail(f"mapping keys mismatch: {sorted(out.keys())}")
    if out["runtime_active"] is not False:
        fail("mapping runtime_active must be False")
    if out["contract_version"] != "status_effect_runtime_adapter_stub_v1":
        fail("mapping contract_version mismatch")
    # invalid input must raise
    try:
        mod.build_status_mapping("x", "bad_cat", "positive", "none", "normal", False, "buff_icon")
        fail("build_status_mapping must raise on invalid category")
    except ValueError:
        pass

    # no import in any watched file
    for f in WATCH_FILES:
        if f.exists() and NEEDLE in f.read_text():
            fail(f"adapter imported by watched file: {f}")
    for f in ROUTES.glob("*.py"):
        if NEEDLE in f.read_text():
            fail(f"adapter imported in routes: {f}")

    print("[PASS] PROJECT_D Track C status effect adapter skeleton OK: contracts valid; NOT imported by battle/runtime")
    sys.exit(0)

if __name__ == "__main__": main()
