#!/usr/bin/env python3
"""PROJECT_C Track C validator (read-only)."""
import json, sys
from pathlib import Path

BASELINE = Path("/app/data/design/status_effects/project_c_status_effect_catalog_baseline_v1.json")


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def main():
    if not BASELINE.exists(): fail(f"missing {BASELINE}")
    m = json.loads(BASELINE.read_text())
    if m.get("verdict") != "TRACK_C_STATUS_EFFECT_CATALOG_BASELINE_READY":
        fail("verdict mismatch")
    if m.get("status_effects_runtime_active") is not False:
        fail("status_effects_runtime_active must be False")
    cats = m.get("canonical_categories", [])
    if len(cats) != 10: fail(f"expected 10 categories, got {len(cats)}")
    eff = m.get("effects_baseline", [])
    if len(eff) != 10: fail(f"expected 10 effects, got {len(eff)}")
    cat_ids = {c["id"] for c in cats}
    for e in eff:
        if e.get("category") not in cat_ids:
            fail(f"effect {e.get('id')} category {e.get('category')} not in canonical set")
        if not (1 <= e.get("duration_turns", 0) <= 10):
            fail(f"effect {e.get('id')} duration_turns out of [1..10]")
        if not (1 <= e.get("stack_max", 0) <= 5):
            fail(f"effect {e.get('id')} stack_max out of [1..5]")
        if not (-50 <= e.get("value_pct", 0) <= 50):
            fail(f"effect {e.get('id')} value_pct out of [-50..50]")
    forb = m.get("forbidden_in_track_c_respected", {})
    for k in ("status_effect_runtime_application", "battle_engine_changes", "combat_tsx_changes", "borea_activation"):
        if forb.get(k) is not False: fail(f"forbidden_in_track_c.{k} must be False")
    print("[PASS] PROJECT_C Track C status effect catalog OK: 10 categories + 10 effects baseline, anti-power-creep caps enforced")
    sys.exit(0)

if __name__ == "__main__": main()
