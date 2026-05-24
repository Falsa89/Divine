#!/usr/bin/env python3
"""PROJECT_C Track H validator (read-only).

Verifica:
- marker JSON con verdict e user_approval scope
- stub `artifact_bonus_resolver_stub.py` presente, pure, e NON importato
  da nessun file in /app/backend/server.py o /app/backend/routes/*.py
- contratto: resolve_artifact_bonus restituisce envelope zero-bonus stabile
- validate_caps_definition ritorna True

Exit 0 PASS / 1 FAIL.
"""
import importlib.util
import json
import sys
from pathlib import Path

MARKER = Path("/app/data/design/artifacts/project_c_artifact_bible_user_approval_and_bonus_resolver_design_v1.json")
STUB = Path("/app/backend/game_logic/artifact_bonus_resolver_stub.py")
WATCH_FILES = [Path("/app/backend/server.py")]
ROUTES_DIR = Path("/app/backend/routes")
UPSTREAM_SCHEMA = Path("/app/data/design/artifacts/artifact_bible_schema_v1.json")
UPSTREAM_CANDIDATES = Path("/app/data/design/artifacts/artifact_bible_launch_candidates_v1.json")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not MARKER.exists():
        fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_H_ARTIFACT_BIBLE_V1_USER_APPROVAL_AND_BONUS_RESOLVER_STUB_DESIGN_READY":
        fail(f"verdict mismatch: {m.get('verdict')}")
    if m.get("runtime_patch_applied") is not False:
        fail("runtime_patch_applied must be False")
    if m.get("artifact_live_bonus_applied") is not False:
        fail("artifact_live_bonus_applied must be False")
    if m.get("artifact_summon_behavior_mutated") is not False:
        fail("artifact_summon_behavior_mutated must be False")
    ua = m.get("user_approval_marker", {})
    if ua.get("artifact_bible_v1_approved") is not True:
        fail("user_approval_marker.artifact_bible_v1_approved must be True")
    if "live_bonus_application" not in ua.get("NOT_in_scope_of_approval", []):
        fail("user_approval must explicitly exclude live_bonus_application")
    phases = m.get("integration_phases", [])
    if len(phases) < 6:
        fail("integration_phases must include 6 entries")
    phase6 = phases[5]
    if phase6.get("status") != "FORBIDDEN_OUT_OF_SCOPE_PROJECT_C":
        fail("phase 6 (LIVE_BONUS_APPLICATION) must be FORBIDDEN_OUT_OF_SCOPE_PROJECT_C")
    forb = m.get("forbidden_in_track_h_respected", {})
    for k in ("artifact_live_bonus", "artifact_summon_behavior_change", "db_migration", "frontend_artifact_ui_rollout", "runtime_import_of_stub"):
        if forb.get(k) is not False:
            fail(f"forbidden_in_track_h.{k} must be False")
    if not STUB.exists():
        fail("stub missing")
    needle = "artifact_bonus_resolver_stub"
    for f in WATCH_FILES:
        if f.exists() and needle in f.read_text():
            fail(f"runtime import detected: {f}")
    for f in ROUTES_DIR.glob("*.py"):
        if needle in f.read_text():
            fail(f"runtime import in routes: {f}")
    # Smoke contract: importa modulo e verifica contratti.
    spec = importlib.util.spec_from_file_location("_proj_c_artifact_stub", STUB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    env = mod.resolve_artifact_bonus([])
    expected_keys = {"hp_pct", "atk_pct", "def_pct", "crit_pct", "source"}
    if set(env.keys()) != expected_keys:
        fail(f"envelope keys mismatch: {set(env.keys())}")
    for k in ("hp_pct", "atk_pct", "def_pct", "crit_pct"):
        if env[k] != 0:
            fail(f"envelope {k} must be 0 in V_C")
    if env["source"] != "resolver_stub_inert":
        fail("envelope source must be resolver_stub_inert")
    env2 = mod.resolve_artifact_bonus(None)
    if env2 != env:
        fail("resolver not stable with None input")
    if mod.validate_caps_definition() is not True:
        fail("validate_caps_definition must return True")
    if not UPSTREAM_SCHEMA.exists() or not UPSTREAM_CANDIDATES.exists():
        fail("upstream artifact bible schema/candidates missing")
    print("[PASS] PROJECT_C Track H artifact bible user approval + bonus resolver stub OK: user-approved schema+candidates; stub pure; NOT imported by runtime; zero-bonus stable")
    sys.exit(0)


if __name__ == "__main__":
    main()
