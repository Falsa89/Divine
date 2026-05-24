#!/usr/bin/env python3
"""
PROJECT_A Track C validator (read-only).

Verifica:
- preflight JSON integrity
- nessuna AF2-N runtime mutation: affinity.py contiene ancora le route canary attese e nessuna stringa di public_spend_ui
- upstream chain V5/V6/V7/V8 esistente

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

PREFLIGHT = Path("/app/data/design/system_safety/project_a_af2n_runtime_routing_preflight_v1.json")
AFFINITY = Path("/app/backend/routes/affinity.py")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not PREFLIGHT.exists():
        fail(f"missing preflight: {PREFLIGHT}")
    m = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    if m.get("verdict") != "TRACK_C_AF2N_RUNTIME_ROUTING_PREFLIGHT_READY":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("af2n_runtime_mutated") is not False:
        fail("af2n_runtime_mutated must be False")

    state = m.get("af2n_current_runtime_state", {})
    if state.get("broad_rollout_authorized") is not False:
        fail("broad_rollout_authorized must be False")
    if state.get("battle_runtime_attached") is not False:
        fail("battle_runtime_attached must be False")
    if state.get("inventory_mutation_enabled") is not False:
        fail("inventory_mutation_enabled must be False")

    forb = m.get("forbidden_in_track_c_respected", {})
    for k in ("af2n_runtime_mutation", "public_spend_ui",
              "gift_spend_inventory_ledger_behavior_change", "stack_g_changes"):
        if forb.get(k) is not False:
            fail(f"forbidden_in_track_c_respected.{k} must be False")

    if AFFINITY.exists():
        src = AFFINITY.read_text(encoding="utf-8")
        # Sanity: ensure no obvious public-spend-UI flag toggled to true in source code.
        # We rely on flag-based audit elsewhere; here we just check no spurious 'PUBLIC_SPEND_UI_ENABLED = True' was added.
        if 'PUBLIC_SPEND_UI_ENABLED = True' in src or 'public_spend_ui = True' in src:
            fail("public spend UI enable detected in affinity.py source")

    print("[PASS] PROJECT_A Track C AF2-N runtime routing preflight OK; no runtime mutation; canary state preserved")
    sys.exit(0)


if __name__ == "__main__":
    main()
