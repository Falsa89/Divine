#!/usr/bin/env python3
"""PROJECT_D Track H validator (read-only).

Valida il freeze design-only dell'Artifact Bible V1:
- marker JSON con verdict atteso
- 7 freeze invariants tutti True
- upstream schema + candidates + V_C approval marker presenti
- resolver stub presente e NOT imported
- 5 launch candidates
Exit 0 PASS / 1 FAIL.
"""
import json, sys
from pathlib import Path

MARKER = Path("/app/data/design/artifacts/project_d_artifact_bible_v1_approval_freeze_pack.json")
SCHEMA = Path("/app/data/design/artifacts/artifact_bible_schema_v1.json")
CANDIDATES = Path("/app/data/design/artifacts/artifact_bible_launch_candidates_v1.json")
V_C_APPROVAL = Path("/app/data/design/artifacts/project_c_artifact_bible_user_approval_and_bonus_resolver_design_v1.json")
STUB = Path("/app/backend/game_logic/artifact_bonus_resolver_stub.py")
ROUTES = Path("/app/backend/routes")
SERVER = Path("/app/backend/server.py")
NEEDLE = "artifact_bonus_resolver_stub"


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_H_ARTIFACT_BIBLE_V1_FROZEN_DESIGN_ONLY":
        fail(f"verdict mismatch: {m.get('verdict')}")
    if m.get("runtime_patch_applied") is not False: fail("runtime_patch_applied must be False")
    if m.get("artifact_live_bonus_active") is not False: fail("artifact_live_bonus_active must be False")
    if m.get("artifact_summon_behavior_active") is not False: fail("artifact_summon_behavior_active must be False")

    fi = m.get("freeze_invariants_checked", {})
    for k in ("not_equipment", "no_gear_slot", "not_divine_weapon",
              "no_unique_weapon_overlap", "no_live_bonus", "bonus_caps_present", "candidates_are_draft"):
        if fi.get(k) is not True: fail(f"freeze_invariants.{k} must be True")

    forb = m.get("forbidden_in_track_h_respected", {})
    for k in ("artifact_live_bonus", "artifact_summon_behavior", "gacha_pity_rate_change", "frontend", "db_writes", "equipment_semantics"):
        if forb.get(k) is not False: fail(f"forbidden_in_track_h.{k} must be False")

    # Upstream artifacts must exist
    for p in (SCHEMA, CANDIDATES, V_C_APPROVAL, STUB):
        if not p.exists(): fail(f"upstream missing: {p}")

    # 5 candidates exact
    candidates = json.loads(CANDIDATES.read_text())
    cand_list = candidates.get("candidates", [])
    if len(cand_list) != 5: fail(f"launch candidates must be exactly 5, got {len(cand_list)}")
    if candidates.get("total_candidates") != 5:
        fail(f"total_candidates must be 5, got {candidates.get('total_candidates')}")

    # V_C approval marker must declare bible v1 approved
    vc = json.loads(V_C_APPROVAL.read_text())
    if vc.get("user_approval_marker", {}).get("artifact_bible_v1_approved") is not True:
        fail("V_C user_approval_marker.artifact_bible_v1_approved must be True (upstream)")

    # Stub NOT imported by runtime
    if SERVER.exists() and NEEDLE in SERVER.read_text():
        fail(f"stub imported by server.py")
    for f in ROUTES.glob("*.py"):
        if NEEDLE in f.read_text():
            fail(f"stub imported in routes: {f}")

    # Stub contract check
    import importlib.util
    spec = importlib.util.spec_from_file_location("_proj_d_artifact_stub", STUB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    env = mod.resolve_artifact_bonus([])
    for k in ("hp_pct", "atk_pct", "def_pct", "crit_pct"):
        if env.get(k) != 0: fail(f"stub envelope {k} must be 0")
    if env.get("source") != "resolver_stub_inert": fail("stub source mismatch")

    print("[PASS] PROJECT_D Track H artifact bible V1 frozen design-only OK: 7 freeze invariants; 5 draft candidates; stub NOT imported; envelope zero-bonus stable")
    sys.exit(0)

if __name__ == "__main__": main()
