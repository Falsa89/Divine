#!/usr/bin/env python3
"""
PROJECT_B Track G validator (read-only).

Verifica struttura del flow matrix QA mobile smoke. NON esegue HTTP nella suite
(eviterebbe accoppiamento con il backend live e ridondanza con altri validator).

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

FLOW = Path("/app/data/design/project_management/project_b_qa_release_mobile_smoke_flow_v1.json")
REQUIRED_STEP_NAMES = {
    "LOGIN", "HEROES_CATALOG", "BOREA_INERT", "PRIMORDIAL_GAIA_INERT",
    "GACHA_SUMMON_PEEK", "BATTLE_ENTRY_DRY", "POST_BATTLE_SUMMARY",
    "MENU_NAV_HOME", "SLC_GUARD_LEGACY_SERVER_SELECT", "SLC_GUARD_NEW_DUAL_ROUTE",
    "AF2N_CANARY_STATUS_GUARD",
}


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not FLOW.exists():
        fail(f"missing flow: {FLOW}")
    m = json.loads(FLOW.read_text(encoding="utf-8"))
    if m.get("verdict") != "TRACK_G_QA_RELEASE_MOBILE_SMOKE_FLOW_READY":
        fail(f"unexpected verdict: {m.get('verdict')}")
    steps = m.get("smoke_flow_matrix", [])
    if len(steps) < 11:
        fail(f"expected >=11 smoke steps, got {len(steps)}")
    names = {s.get("name") for s in steps}
    missing = REQUIRED_STEP_NAMES - names
    if missing:
        fail(f"missing required step names: {sorted(missing)}")
    if m.get("mutating_step_count", 0) > 1:
        fail("more than 1 mutating step is not allowed in smoke matrix")
    if not isinstance(m.get("excludes"), list) or "graphics_finalization" not in m.get("excludes", []):
        fail("excludes must contain 'graphics_finalization'")

    forb = m.get("forbidden_in_track_g_respected", {})
    for k in ("frontend_implementation", "runtime_behavior_changes",
              "real_gacha_spend", "battle_behavior_mutation"):
        if forb.get(k) is not False:
            fail(f"forbidden_in_track_g_respected.{k} must be False")

    print(f"[PASS] PROJECT_B Track G QA mobile smoke flow OK: {len(steps)} steps, mutating={m.get('mutating_step_count')}")
    sys.exit(0)


if __name__ == "__main__":
    main()
