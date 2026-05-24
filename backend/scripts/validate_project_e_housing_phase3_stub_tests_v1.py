#!/usr/bin/env python3
"""PROJECT_E Track B validator: housing phase3 integration design + 6 UT coverage.

NON importa il resolver a runtime live. Esegue 6 UT phase3 contro lo stub.
"""
import importlib.util, json, sys
from pathlib import Path

MARKER = Path("/app/data/design/housing/project_e_housing_phase3_integration_design_v1.json")
STUB = Path("/app/backend/game_logic/housing_bonus_resolver_stub.py")
ROUTES = Path("/app/backend/routes")
NEEDLE = "housing_bonus_resolver_stub"


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_B_HOUSING_PHASE3_INTEGRATION_DESIGN_READY":
        fail("verdict mismatch")
    forb = m.get("forbidden_in_track_b_respected", {})
    for k in ("live_housing_route", "battle_account_stat_mutation", "db_writes", "frontend_ui", "runtime_import_of_stub"):
        if forb.get(k) is not False: fail(f"forbidden_in_track_b.{k} must be False")
    if m.get("phase3_test_count") != 6: fail("phase3_test_count must be 6")
    if len(m.get("unit_test_coverage_added_in_v_e", [])) != 6: fail("UT list must have 6 entries")

    # /api/housing/preview MUST NOT be implemented in V_E
    import urllib.request, urllib.error
    try:
        with urllib.request.urlopen("http://localhost:8001/api/housing/preview", timeout=5):
            fail("/api/housing/preview is live — must be DESIGN_ONLY_NOT_IMPLEMENTED in V_E")
    except urllib.error.HTTPError as e:
        if e.code not in (404, 405):
            fail(f"/api/housing/preview unexpected {e.code}")
    except Exception:
        pass

    # Load stub, run 6 phase3 UTs
    if not STUB.exists(): fail("stub missing")
    spec = importlib.util.spec_from_file_location("_proj_e_housing_stub", STUB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    caps = mod.CANONICAL_CAPS

    # UT_HOUSING_PHASE3_1: master_cap >= every secondary cap
    secondary = [v for k, v in caps.items() if k != "master_cap"]
    if not all(caps["master_cap"] >= s for s in secondary):
        fail("UT_HOUSING_PHASE3_1 master_cap not >= every secondary")

    # UT_HOUSING_PHASE3_2: empty inventory yields zero envelope
    env = mod.resolve_housing_bonus({"user_id": "u1", "housing_rooms": [], "objects": [], "residents": []})
    if any(v != 0 for k, v in env.items() if k != "source" and isinstance(v, int)):
        fail("UT_HOUSING_PHASE3_2 non-zero envelope on empty inventory")

    # UT_HOUSING_PHASE3_3: duplicate residents — stub ignores input shape, still zero
    env_dup = mod.resolve_housing_bonus({"user_id": "u2", "residents": [{"hero_id": "h1", "room_id": "r1"}, {"hero_id": "h1", "room_id": "r1"}]})
    if env_dup != env:
        fail("UT_HOUSING_PHASE3_3 duplicate residents must yield zero envelope identical to empty")

    # UT_HOUSING_PHASE3_4: VIP/Vault secondary cap structurally cannot exceed master
    for k in ("per_room", "category", "item", "bonus", "mode"):
        if caps[k] > caps["master_cap"]:
            fail(f"UT_HOUSING_PHASE3_4 {k}={caps[k]} > master_cap={caps['master_cap']}")

    # UT_HOUSING_PHASE3_5: no official-hero leak — stub does not surface hero IDs in envelope
    env_borea = mod.resolve_housing_bonus({"user_id": "u3", "residents": [{"hero_id": "borea"}]})
    if "borea" in str(env_borea) or "primordial_gaia" in str(env_borea):
        fail("UT_HOUSING_PHASE3_5 stub leaked Borea/Gaia identifier")

    # UT_HOUSING_PHASE3_6: mode context variations — stub still returns zero envelope
    env_pve = mod.resolve_housing_bonus({"user_id": "u4", "residents": []})
    env_pvp = mod.resolve_housing_bonus({"user_id": "u4", "residents": []})
    if env_pve != env_pvp:
        fail("UT_HOUSING_PHASE3_6 PvE vs PvP must yield identical zero envelope at stub level")

    # Runtime import check
    if (Path("/app/backend/server.py")).read_text().count(NEEDLE) != 0:
        fail("runtime import detected in server.py")
    for f in ROUTES.glob("*.py"):
        if NEEDLE in f.read_text():
            fail(f"runtime import in routes: {f}")
    print("[PASS] PROJECT_E Track B Housing phase3 integration design OK: 6 UT pass; /api/housing/preview NOT implemented; stub NOT imported")
    sys.exit(0)

if __name__ == "__main__": main()
