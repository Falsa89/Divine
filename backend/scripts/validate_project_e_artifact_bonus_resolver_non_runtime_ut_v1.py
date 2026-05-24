#!/usr/bin/env python3
"""PROJECT_E Track G validator: artifact bonus resolver non-runtime UT."""
import importlib.util, json, sys
from pathlib import Path

MARKER = Path("/app/data/design/artifacts/project_e_artifact_bonus_resolver_non_runtime_ut_v1.json")
STUB = Path("/app/backend/game_logic/artifact_bonus_resolver_stub.py")
CANDIDATES = Path("/app/data/design/artifacts/artifact_bible_launch_candidates_v1.json")
FREEZE = Path("/app/data/design/artifacts/project_d_artifact_bible_v1_approval_freeze_pack.json")
ROUTES = Path("/app/backend/routes")
SERVER = Path("/app/backend/server.py")
NEEDLE = "artifact_bonus_resolver_stub"


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_G_ARTIFACT_BONUS_RESOLVER_UT_READY": fail("verdict mismatch")
    if m.get("unit_test_count") != 6: fail("unit_test_count must be 6")
    forb = m.get("forbidden_in_track_g_respected", {})
    for k in ("artifact_live_bonus", "artifact_summon", "gacha_rate_pity_change", "frontend", "db_writes", "equipment_semantics"):
        if forb.get(k) is not False: fail(f"forbidden_in_track_g.{k} must be False")
    for p in (STUB, CANDIDATES, FREEZE):
        if not p.exists(): fail(f"upstream missing: {p}")

    spec = importlib.util.spec_from_file_location("_proj_e_artifact", STUB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # UT_ARTIFACT_1: zero envelope con 5 chiavi
    env = mod.resolve_artifact_bonus([])
    expected_keys = {"hp_pct", "atk_pct", "def_pct", "crit_pct", "source"}
    if set(env.keys()) != expected_keys: fail(f"UT_ARTIFACT_1 keys mismatch: {sorted(env.keys())}")
    for k in ("hp_pct", "atk_pct", "def_pct", "crit_pct"):
        if env[k] != 0: fail(f"UT_ARTIFACT_1 {k} must be 0")

    # UT_ARTIFACT_2: caps definite per ogni componente; documentati nello stub
    caps = getattr(mod, "ARTIFACT_BONUS_CAPS", None)
    if caps is None: fail("UT_ARTIFACT_2 ARTIFACT_BONUS_CAPS missing")
    for k in ("hp_pct", "atk_pct", "def_pct", "crit_pct"):
        if k not in caps: fail(f"UT_ARTIFACT_2 caps missing {k}")
        if caps[k]["min"] >= caps[k]["max"]: fail(f"UT_ARTIFACT_2 caps {k} min>=max")

    # UT_ARTIFACT_3 + UT_ARTIFACT_4: candidates non-equipment + draft
    cands = json.loads(CANDIDATES.read_text())
    for c in cands.get("candidates", []):
        if c.get("slot") in ("weapon", "armor", "helmet", "boots", "gloves", "accessory"):
            fail(f"UT_ARTIFACT_3 candidate has equipment slot: {c}")
        if c.get("status", "draft") != "draft":
            fail(f"UT_ARTIFACT_4 candidate not draft: {c}")

    # UT_ARTIFACT_5: stub NOT imported
    if SERVER.exists() and NEEDLE in SERVER.read_text(): fail("UT_ARTIFACT_5 stub imported in server.py")
    for f in ROUTES.glob("*.py"):
        if NEEDLE in f.read_text(): fail(f"UT_ARTIFACT_5 stub imported in routes: {f}")

    # UT_ARTIFACT_6: validate_caps_definition() True
    if mod.validate_caps_definition() is not True: fail("UT_ARTIFACT_6 validate_caps_definition must return True")

    print("[PASS] PROJECT_E Track G artifact bonus resolver non-runtime UT OK: 6/6 UT pass; stub NOT imported; candidates DRAFT non-equipment")
    sys.exit(0)

if __name__ == "__main__": main()
